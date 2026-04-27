from django.db import transaction

from apps.cart.models import CartItem, PackageDraft
from apps.orders.models import (
    Order,
    OrderCustomPackage,
    OrderCustomPackageItem,
    OrderItem,
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


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user):
        cart_items = CartItem.objects.filter(user=user).select_related("product", "pickup_store")
        package_drafts = (
            PackageDraft.objects.filter(user=user)
            .exclude(status=PackageDraft.Status.ORDERED)
            .select_related("policy", "pickup_store")
            .prefetch_related("items__product")
        )

        if not cart_items.exists() and not package_drafts.exists():
            raise CartIsEmptyError("장바구니가 비어있습니다.")

        total_price = sum(item.total_price for item in cart_items) + sum(draft.final_price for draft in package_drafts)

        # 1. 주문 생성
        order = Order.objects.create(user=user, total_price=total_price)

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

        # 3. 장바구니 비우기
        cart_items.delete()
        package_drafts.update(status=PackageDraft.Status.ORDERED)

        return order

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
