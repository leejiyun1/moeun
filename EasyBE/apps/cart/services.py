from django.db import transaction

from apps.products.models import PackagePolicy, Product

from .models import CartItem, PackageDraft, PackageDraftItem


class PackageDraftValidationError(ValueError):
    """커스텀 패키지 draft 검증 실패."""


class CartValidationError(ValueError):
    """일반 장바구니 항목 검증 실패."""


class CartService:
    @staticmethod
    def add_or_update_item(user, product_id, quantity, pickup_store, pickup_date):
        """
        장바구니에 상품을 추가하거나, 이미 있는 경우 수량을 업데이트합니다.
        """
        if quantity < 1:
            raise CartValidationError("장바구니에 추가할 수량은 1 이상이어야 합니다.")

        try:
            product = Product.objects.get(id=product_id, status=Product.Status.ACTIVE)
        except Product.DoesNotExist as exc:
            raise CartValidationError("존재하지 않거나 비활성 상태인 상품입니다.") from exc

        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            pickup_store=pickup_store,
            pickup_date=pickup_date,
            defaults={"quantity": quantity},
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    @staticmethod
    def update_item(cart_item, data):
        """
        장바구니 상품의 수량/픽업 정보를 업데이트합니다. 수량이 0이면 삭제합니다.
        """
        quantity = data.get("quantity")
        if quantity == 0:
            cart_item.delete()
            return None

        update_fields = []
        if quantity is not None:
            if quantity < 0:
                raise CartValidationError("수량은 0 이상이어야 합니다.")
            cart_item.quantity = quantity
            update_fields.append("quantity")

        if "pickup_store" in data:
            cart_item.pickup_store = data["pickup_store"]
            update_fields.append("pickup_store")
        if "pickup_date" in data:
            cart_item.pickup_date = data["pickup_date"]
            update_fields.append("pickup_date")

        if update_fields:
            cart_item.save(update_fields=[*update_fields, "updated_at"])
        return cart_item

    @staticmethod
    def get_cart_info(user):
        """
        사용자의 장바구니 정보(항목 목록, 총액)를 반환합니다.
        """
        cart_items = (
            CartItem.objects.filter(user=user)
            .select_related("product", "pickup_store")
            .prefetch_related("product__images", "product__drink", "product__package")
        )
        package_drafts = CartPackageDraftService.get_user_drafts(user)
        total_price = sum(item.total_price for item in cart_items) + sum(draft.final_price for draft in package_drafts)
        return cart_items, package_drafts, total_price


class CartPackageDraftService:
    """장바구니 커스텀 패키지 draft write/read 서비스."""

    @staticmethod
    def get_user_drafts(user):
        return (
            PackageDraft.objects.filter(user=user)
            .exclude(status=PackageDraft.Status.ORDERED)
            .select_related("policy", "pickup_store")
            .prefetch_related("items__product__images", "items__product__drink", "items__product__package")
            .order_by("-created_at")
        )

    @staticmethod
    @transaction.atomic
    def create_draft(
        *,
        user,
        policy_id: int,
        display_name: str,
        items: list[dict],
        pickup_store=None,
        pickup_date=None,
        is_tasting_selected: bool = False,
    ) -> PackageDraft:
        policy = CartPackageDraftService._get_policy(policy_id)
        normalized_items = CartPackageDraftService._normalize_items(items)
        products_by_id = CartPackageDraftService._get_active_products_by_id(
            [item["product_id"] for item in normalized_items]
        )
        CartPackageDraftService._validate_policy(policy, normalized_items, products_by_id)
        prices = CartPackageDraftService._calculate_prices(policy, normalized_items, products_by_id)

        draft = PackageDraft.objects.create(
            user=user,
            policy=policy,
            display_name=display_name.strip(),
            pickup_store=pickup_store,
            pickup_date=pickup_date,
            is_tasting_selected=is_tasting_selected,
            **prices,
        )
        CartPackageDraftService._create_items(draft, normalized_items, products_by_id)
        return draft

    @staticmethod
    @transaction.atomic
    def update_draft(draft: PackageDraft, data: dict) -> PackageDraft:
        data = dict(data)
        items = data.pop("items", None)
        policy_id = data.pop("policy_id", None)

        policy = CartPackageDraftService._get_policy(policy_id) if policy_id is not None else draft.policy
        normalized_items = (
            CartPackageDraftService._normalize_items(items)
            if items is not None
            else [
                {"product_id": str(item.product_id), "quantity": item.quantity, "sort_order": item.sort_order}
                for item in draft.items.all()
            ]
        )
        products_by_id = CartPackageDraftService._get_active_products_by_id(
            [item["product_id"] for item in normalized_items]
        )
        CartPackageDraftService._validate_policy(policy, normalized_items, products_by_id)
        prices = CartPackageDraftService._calculate_prices(policy, normalized_items, products_by_id)

        for field, value in data.items():
            if field == "display_name" and isinstance(value, str):
                value = value.strip()
            setattr(draft, field, value)
        draft.policy = policy
        draft.base_price = prices["base_price"]
        draft.discount_amount = prices["discount_amount"]
        draft.final_price = prices["final_price"]
        draft.save()

        if items is not None:
            draft.items.all().delete()
            CartPackageDraftService._create_items(draft, normalized_items, products_by_id)

        return draft

    @staticmethod
    def _get_policy(policy_id: int) -> PackagePolicy:
        try:
            return PackagePolicy.objects.get(id=policy_id, status=PackagePolicy.Status.ACTIVE)
        except PackagePolicy.DoesNotExist as exc:
            raise PackageDraftValidationError("존재하지 않거나 비활성 상태인 패키지 정책입니다.") from exc

    @staticmethod
    def _normalize_items(items: list[dict]) -> list[dict]:
        if not items:
            raise PackageDraftValidationError("패키지 구성은 필수입니다.")

        merged_items = {}
        sort_orders = {}
        for index, item in enumerate(items):
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            sort_order = item.get("sort_order", index)

            if not isinstance(product_id, str):
                raise PackageDraftValidationError("product_id는 문자열 UUID여야 합니다.")
            if not isinstance(quantity, int) or quantity < 1:
                raise PackageDraftValidationError("quantity는 1 이상의 정수여야 합니다.")
            if not isinstance(sort_order, int) or sort_order < 0:
                raise PackageDraftValidationError("sort_order는 0 이상의 정수여야 합니다.")

            merged_items[product_id] = merged_items.get(product_id, 0) + quantity
            sort_orders.setdefault(product_id, sort_order)

        return [
            {"product_id": product_id, "quantity": quantity, "sort_order": sort_orders[product_id]}
            for product_id, quantity in merged_items.items()
        ]

    @staticmethod
    def _get_active_products_by_id(product_ids: list[str]) -> dict[str, Product]:
        products_by_id = {
            str(product.id): product
            for product in Product.objects.filter(id__in=product_ids, status=Product.Status.ACTIVE).select_related(
                "drink", "package"
            )
        }
        if len(products_by_id) != len(set(product_ids)):
            raise PackageDraftValidationError("존재하지 않거나 비활성 상태인 상품이 포함되어 있습니다.")
        return products_by_id

    @staticmethod
    def _validate_policy(policy: PackagePolicy, items: list[dict], products_by_id: dict[str, Product]) -> None:
        total_quantity = sum(item["quantity"] for item in items)
        if not policy.min_items <= total_quantity <= policy.max_items:
            raise PackageDraftValidationError(
                f"패키지 총 구성 수량은 {policy.min_items}~{policy.max_items}개여야 합니다."
            )
        if not policy.allow_duplicate_items and any(item["quantity"] > 1 for item in items):
            raise PackageDraftValidationError("이 패키지 정책은 같은 상품 중복 구성을 허용하지 않습니다.")

        selected_products = [products_by_id[item["product_id"]] for item in items]
        if policy.allowed_item_scope == PackagePolicy.AllowedItemScope.SINGLE_PRODUCTS:
            if any(product.drink_id is None for product in selected_products):
                raise PackageDraftValidationError("이 패키지 정책은 단일 상품만 허용합니다.")
        elif policy.allowed_item_scope == PackagePolicy.AllowedItemScope.PACKAGE_PRODUCTS:
            if any(product.package_id is None for product in selected_products):
                raise PackageDraftValidationError("이 패키지 정책은 패키지 상품만 허용합니다.")
        elif policy.allowed_item_scope == PackagePolicy.AllowedItemScope.ALLOWED_SET:
            allowed_ids = {str(product_id) for product_id in policy.allowed_products.values_list("id", flat=True)}
            selected_ids = {str(product.id) for product in selected_products}
            if not selected_ids.issubset(allowed_ids):
                raise PackageDraftValidationError("패키지 정책에서 허용하지 않은 상품이 포함되어 있습니다.")

    @staticmethod
    def _calculate_prices(policy: PackagePolicy, items: list[dict], products_by_id: dict[str, Product]) -> dict:
        base_price = sum(products_by_id[item["product_id"]].price * item["quantity"] for item in items)
        discount_amount = 0
        if policy.discount_type == PackagePolicy.DiscountType.FIXED_AMOUNT:
            discount_amount = min(policy.discount_value, base_price)
        return {
            "base_price": base_price,
            "discount_amount": discount_amount,
            "final_price": base_price - discount_amount,
        }

    @staticmethod
    def _create_items(draft: PackageDraft, items: list[dict], products_by_id: dict[str, Product]) -> None:
        PackageDraftItem.objects.bulk_create(
            [
                PackageDraftItem(
                    draft=draft,
                    product=products_by_id[item["product_id"]],
                    quantity=item["quantity"],
                    sort_order=item["sort_order"],
                )
                for item in items
            ]
        )
