import base64

import requests
from django.conf import settings
from django.db import transaction

from apps.cart.models import CartItem, PackageDraft
from apps.orders.models import (
    Order,
    OrderCustomPackage,
    OrderCustomPackageItem,
    OrderItem,
    Payment,
)
from apps.stores.models import Store


class OrderCreationError(Exception):
    """주문 생성 관련 최상위 예외"""

    pass


class CartIsEmptyError(OrderCreationError):
    """장바구니가 비어있을 때 발생하는 예외"""

    pass


class MissingPickupInfoError(OrderCreationError):
    """픽업 정보가 누락되었을 때 발생하는 예외"""

    pass


class InvalidCartSelectionError(OrderCreationError):
    """선택한 장바구니 항목이 유효하지 않을 때 발생하는 예외"""

    pass


class AdultVerificationRequiredError(OrderCreationError):
    """성인 인증이 필요한 주문일 때 발생하는 예외"""

    pass


class PaymentError(OrderCreationError):
    """결제 처리 중 발생하는 예외"""

    pass


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(
        user,
        cart_item_ids=None,
        package_draft_ids=None,
        fulfillment_method=Order.FulfillmentMethod.PICKUP,
        pickup_store_id=None,
        pickup_date=None,
        is_test_order=True,
        payment_provider=Payment.Provider.TOSS_TEST,
    ):
        if not user.is_adult:
            raise AdultVerificationRequiredError("주문 전 성인 인증이 필요합니다.")

        if fulfillment_method not in Order.FulfillmentMethod.values:
            raise OrderCreationError("지원하지 않는 수령 방식입니다.")

        cart_items = CartItem.objects.filter(user=user).select_related("product")
        package_drafts = (
            PackageDraft.objects.filter(user=user)
            .exclude(status=PackageDraft.Status.ORDERED)
            .select_related("policy")
            .prefetch_related("items__product")
        )
        if cart_item_ids is not None:
            cart_items = OrderService._filter_selected_cart_items(cart_items, cart_item_ids)
        if package_draft_ids is not None:
            package_drafts = OrderService._filter_selected_package_drafts(package_drafts, package_draft_ids)

        if not cart_items.exists() and not package_drafts.exists():
            raise CartIsEmptyError("장바구니가 비어있습니다.")

        pickup_store = OrderService._resolve_pickup_store(fulfillment_method, pickup_store_id, pickup_date)

        total_price = sum(item.total_price for item in cart_items) + sum(draft.final_price for draft in package_drafts)

        # 1. 주문 생성
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            fulfillment_method=fulfillment_method,
            pickup_store=pickup_store,
            pickup_day=pickup_date if fulfillment_method == Order.FulfillmentMethod.PICKUP else None,
            is_test_order=is_test_order,
        )

        # 2. 주문 항목 생성
        order_items_to_create = []
        for item in cart_items:
            order_item = OrderItem(
                order=order,
                product=item.product,
                price=item.product.price,  # 주문 당시 가격 기록
                quantity=item.quantity,
                pickup_store=order.pickup_store,
                pickup_day=order.pickup_day,
            )
            order_items_to_create.append(order_item)

        OrderItem.objects.bulk_create(order_items_to_create)
        OrderService._create_custom_package_snapshots(order, package_drafts)
        OrderService._create_ready_payment(order, payment_provider)

        # 3. 장바구니 비우기
        cart_items.delete()
        package_drafts.update(status=PackageDraft.Status.ORDERED)

        return order

    @staticmethod
    def _resolve_pickup_store(fulfillment_method, pickup_store_id, pickup_date):
        if fulfillment_method != Order.FulfillmentMethod.PICKUP:
            return None
        if not pickup_store_id or not pickup_date:
            raise MissingPickupInfoError("픽업 주문은 픽업 매장과 날짜가 필요합니다.")
        try:
            return Store.objects.get(id=pickup_store_id)
        except Store.DoesNotExist as exc:
            raise MissingPickupInfoError("존재하지 않는 픽업 매장입니다.") from exc

    @staticmethod
    @transaction.atomic
    def confirm_test_payment(user, order_id, payment_key):
        if not payment_key:
            raise PaymentError("테스트 결제 키가 필요합니다.")

        order = Order.objects.select_for_update().filter(id=order_id, user=user).first()
        if order is None:
            raise PaymentError("주문을 찾을 수 없습니다.")
        if not order.is_test_order:
            raise PaymentError("테스트 주문만 테스트 결제로 승인할 수 있습니다.")
        if order.payment_status == Order.PaymentStatus.PAID:
            return order
        if order.status == Order.Status.CANCELLED:
            raise PaymentError("취소된 주문은 결제 승인할 수 없습니다.")

        payment = Payment.objects.select_for_update().filter(order=order).first()
        if payment is None:
            raise PaymentError("결제 정보를 찾을 수 없습니다.")
        if payment.amount != order.total_price:
            raise PaymentError("결제 금액이 주문 금액과 일치하지 않습니다.")

        payment.mark_paid(
            payment_key=payment_key,
            raw_response={
                "provider": Payment.Provider.TEST,
                "payment_key": payment_key,
                "amount": payment.amount,
            },
        )
        order.mark_paid()
        return order

    @staticmethod
    def confirm_toss_payment(user, payment_key, order_id, amount):
        if not settings.TOSS_PAYMENTS_SECRET_KEY:
            raise PaymentError("토스페이먼츠 시크릿 키가 설정되어 있지 않습니다.")

        with transaction.atomic():
            payment = Payment.objects.select_for_update().filter(merchant_uid=order_id, order__user=user).first()
            if payment is None:
                raise PaymentError("결제 정보를 찾을 수 없습니다.")

            order = Order.objects.select_for_update().get(id=payment.order_id)
            if payment.provider != Payment.Provider.TOSS_TEST or not payment.is_test_payment:
                raise PaymentError("토스페이먼츠 테스트 결제만 승인할 수 있습니다.")
            if order.payment_status == Order.PaymentStatus.PAID:
                return order
            if int(amount) != order.total_price:
                payment.mark_failed({"reason": "AMOUNT_MISMATCH", "requested_amount": amount})
                order.payment_status = Order.PaymentStatus.FAILED
                order.save(update_fields=["payment_status", "updated_at"])
                amount_error = "결제 금액이 주문 금액과 일치하지 않습니다."
            else:
                amount_error = None

        if amount_error:
            raise PaymentError(amount_error)

        response = OrderService._request_toss_confirm(
            payment_key=payment_key,
            order_id=order_id,
            amount=order.total_price,
        )
        with transaction.atomic():
            payment = Payment.objects.select_for_update().filter(merchant_uid=order_id, order__user=user).first()
            order = Order.objects.select_for_update().get(id=payment.order_id)
            if order.payment_status == Order.PaymentStatus.PAID:
                return order

            if not response.ok:
                raw_response = OrderService._safe_response_json(response)
                payment.mark_failed(raw_response)
                order.payment_status = Order.PaymentStatus.FAILED
                order.save(update_fields=["payment_status", "updated_at"])
                toss_error = raw_response.get("message", "토스페이먼츠 결제 승인에 실패했습니다.")
            else:
                raw_response = response.json()
                payment.mark_paid(payment_key=payment_key, raw_response=raw_response)
                order.mark_paid()
                toss_error = None

        if toss_error:
            raise PaymentError(toss_error)
        return order

    @staticmethod
    def _filter_selected_cart_items(queryset, cart_item_ids):
        try:
            selected_ids = {int(item_id) for item_id in cart_item_ids}
        except (TypeError, ValueError) as exc:
            raise InvalidCartSelectionError("장바구니 항목 선택값이 올바르지 않습니다.") from exc
        if not selected_ids:
            return queryset.none()

        selected_queryset = queryset.filter(id__in=selected_ids)
        if selected_queryset.count() != len(selected_ids):
            raise InvalidCartSelectionError("선택한 장바구니 항목 중 유효하지 않은 항목이 있습니다.")
        return selected_queryset

    @staticmethod
    def _filter_selected_package_drafts(queryset, package_draft_ids):
        try:
            selected_ids = {int(draft_id) for draft_id in package_draft_ids}
        except (TypeError, ValueError) as exc:
            raise InvalidCartSelectionError("커스텀 패키지 선택값이 올바르지 않습니다.") from exc
        if not selected_ids:
            return queryset.none()

        selected_queryset = queryset.filter(id__in=selected_ids)
        if selected_queryset.count() != len(selected_ids):
            raise InvalidCartSelectionError("선택한 커스텀 패키지 중 유효하지 않은 항목이 있습니다.")
        return selected_queryset

    @staticmethod
    def _create_custom_package_snapshots(order, package_drafts):
        custom_package_items_to_create = []

        for draft in package_drafts:
            custom_package = OrderCustomPackage.objects.create(
                order=order,
                source_draft=draft,
                display_name=draft.display_name,
                package_policy_name=draft.policy.name,
                base_price=draft.base_price,
                discount_amount=draft.discount_amount,
                final_price=draft.final_price,
                pickup_store=order.pickup_store,
                pickup_day=order.pickup_day,
                is_tasting_selected=draft.is_tasting_selected,
            )

            for item in draft.items.all():
                custom_package_items_to_create.append(
                    OrderCustomPackageItem(
                        custom_package=custom_package,
                        product=item.product,
                        product_name=item.product.name,
                        price=item.product.price,
                        quantity=item.quantity,
                        sort_order=item.sort_order,
                    )
                )

        OrderCustomPackageItem.objects.bulk_create(custom_package_items_to_create)

    @staticmethod
    def _create_ready_payment(order, payment_provider):
        return Payment.objects.create(
            order=order,
            provider=payment_provider,
            merchant_uid=order.order_number,
            amount=order.total_price,
            status=Payment.Status.READY,
            is_test_payment=order.is_test_order,
        )

    @staticmethod
    def _request_toss_confirm(payment_key, order_id, amount):
        auth_token = base64.b64encode(f"{settings.TOSS_PAYMENTS_SECRET_KEY}:".encode()).decode()
        return requests.post(
            settings.TOSS_PAYMENTS_CONFIRM_URL,
            headers={
                "Authorization": f"Basic {auth_token}",
                "Content-Type": "application/json",
            },
            json={
                "paymentKey": payment_key,
                "orderId": order_id,
                "amount": amount,
            },
            timeout=10,
        )

    @staticmethod
    def _safe_response_json(response):
        try:
            return response.json()
        except ValueError:
            return {"message": response.text or "토스페이먼츠 응답을 해석할 수 없습니다."}
