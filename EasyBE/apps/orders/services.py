from django.db import transaction

from apps.cart.models import CartItem, PackageDraft
from apps.orders.models import (
    Order,
    OrderCustomPackage,
    OrderCustomPackageItem,
    OrderItem,
    Payment,
)


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
        is_test_order=True,
    ):
        if not user.is_adult:
            raise AdultVerificationRequiredError("주문 전 성인 인증이 필요합니다.")

        if fulfillment_method not in Order.FulfillmentMethod.values:
            raise OrderCreationError("지원하지 않는 수령 방식입니다.")

        cart_items = CartItem.objects.filter(user=user).select_related("product", "pickup_store")
        package_drafts = (
            PackageDraft.objects.filter(user=user)
            .exclude(status=PackageDraft.Status.ORDERED)
            .select_related("policy", "pickup_store")
            .prefetch_related("items__product")
        )
        if cart_item_ids is not None:
            cart_items = OrderService._filter_selected_cart_items(cart_items, cart_item_ids)
        if package_draft_ids is not None:
            package_drafts = OrderService._filter_selected_package_drafts(package_drafts, package_draft_ids)

        if not cart_items.exists() and not package_drafts.exists():
            raise CartIsEmptyError("장바구니가 비어있습니다.")

        total_price = sum(item.total_price for item in cart_items) + sum(draft.final_price for draft in package_drafts)

        # 1. 주문 생성
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            fulfillment_method=fulfillment_method,
            is_test_order=is_test_order,
        )

        # 2. 주문 항목 생성
        order_items_to_create = []
        for item in cart_items:
            if not item.pickup_store or not item.pickup_date:
                raise MissingPickupInfoError(f"{item.product.name} 상품의 픽업 정보가 없습니다.")

            order_item = OrderItem(
                order=order,
                product=item.product,
                price=item.product.price,  # 주문 당시 가격 기록
                quantity=item.quantity,
                pickup_store=item.pickup_store,
                pickup_day=item.pickup_date,
            )
            order_items_to_create.append(order_item)

        OrderItem.objects.bulk_create(order_items_to_create)
        OrderService._create_custom_package_snapshots(order, package_drafts)
        OrderService._create_ready_payment(order)

        # 3. 장바구니 비우기
        cart_items.delete()
        package_drafts.update(status=PackageDraft.Status.ORDERED)

        return order

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
            if not draft.pickup_store or not draft.pickup_date:
                raise MissingPickupInfoError(f"{draft.display_name} 패키지의 픽업 정보가 없습니다.")

            custom_package = OrderCustomPackage.objects.create(
                order=order,
                source_draft=draft,
                display_name=draft.display_name,
                package_policy_name=draft.policy.name,
                base_price=draft.base_price,
                discount_amount=draft.discount_amount,
                final_price=draft.final_price,
                pickup_store=draft.pickup_store,
                pickup_day=draft.pickup_date,
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
    def _create_ready_payment(order):
        return Payment.objects.create(
            order=order,
            provider=Payment.Provider.TEST,
            merchant_uid=f"{order.order_number}-TEST",
            amount=order.total_price,
            status=Payment.Status.READY,
            is_test_payment=order.is_test_order,
        )
