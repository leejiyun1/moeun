from typing import Any

from django.db import transaction

from apps.products.models import (
    Brewery,
    Drink,
    Package,
    PackageItem,
    PackagePolicy,
    Product,
    ProductImage,
)


class ProductCommandService:
    """상품 생성/수정/삭제 write 오케스트레이션."""

    @staticmethod
    @transaction.atomic
    def create_single_product(
        *,
        drink_data: dict[str, Any],
        product_data: dict[str, Any],
        images_data: list[dict[str, Any]],
    ) -> Product:
        drink = ProductCommandService._create_drink(drink_data)
        product = Product.objects.create(drink=drink, **dict(product_data))
        ProductCommandService._create_product_images(product, images_data)
        return product

    @staticmethod
    @transaction.atomic
    def create_package_product(
        *,
        package_data: dict[str, Any],
        product_data: dict[str, Any],
        images_data: list[dict[str, Any]],
    ) -> Product:
        package = ProductCommandService._create_package(package_data)
        product = Product.objects.create(package=package, **dict(product_data))
        ProductCommandService._create_product_images(product, images_data)
        return product

    @staticmethod
    @transaction.atomic
    def deactivate_product(product: Product) -> Product:
        product.status = Product.Status.INACTIVE
        product.save(update_fields=["status", "updated_at"])
        return product

    @staticmethod
    @transaction.atomic
    def update_product(product: Product, product_data: dict[str, Any]) -> Product:
        product_data = dict(product_data)
        images_data = product_data.pop("images", None)
        drink_data = product_data.pop("drink_info", None)
        package_data = product_data.pop("package_info", None)

        if not product_data and images_data is None and drink_data is None and package_data is None:
            return product

        if product_data:
            update_fields = [*product_data.keys(), "updated_at"]
            for field, value in product_data.items():
                setattr(product, field, value)
            product.save(update_fields=update_fields)
        elif images_data is not None:
            product.save(update_fields=["updated_at"])

        if images_data is not None:
            ProductCommandService._replace_product_images(product, images_data)

        if drink_data is not None and product.drink_id:
            ProductCommandService._update_drink(product.drink, drink_data)

        if package_data is not None and product.package_id:
            ProductCommandService._update_package(product.package, package_data)

        return product

    @staticmethod
    def _create_drink(drink_data: dict[str, Any]) -> Drink:
        drink_data = dict(drink_data)
        brewery_id = drink_data.pop("brewery_id")
        brewery = Brewery.objects.get(id=brewery_id)
        return Drink.objects.create(brewery=brewery, **drink_data)

    @staticmethod
    def _create_package(package_data: dict[str, Any]) -> Package:
        package_data = dict(package_data)
        items_data = ProductCommandService._normalize_package_items(package_data)
        policy_id = package_data.pop("policy_id", None)
        policy = ProductCommandService._get_package_policy(policy_id)
        ProductCommandService._validate_package_items(items_data, policy)

        if policy_id is not None:
            package_data["policy_id"] = policy_id

        package = Package.objects.create(**package_data)

        ProductCommandService._create_package_items(package, items_data)
        return package

    @staticmethod
    def _create_product_images(product: Product, images_data: list[dict[str, Any]]) -> None:
        ProductImage.objects.bulk_create(
            [ProductImage(product=product, **dict(image_data)) for image_data in images_data]
        )

    @staticmethod
    def _replace_product_images(product: Product, images_data: list[dict[str, Any]]) -> None:
        product.images.all().delete()
        ProductCommandService._create_product_images(product, images_data)

    @staticmethod
    def _update_drink(drink: Drink, drink_data: dict[str, Any]) -> None:
        drink_data = dict(drink_data)
        update_fields = []

        for field, value in drink_data.items():
            setattr(drink, field, value)
            update_fields.append("brewery" if field == "brewery_id" else field)

        if update_fields:
            drink.save(update_fields=[*update_fields, "updated_at"])

    @staticmethod
    def _update_package(package: Package, package_data: dict[str, Any]) -> None:
        package_data = dict(package_data)
        items_data = ProductCommandService._normalize_package_items(package_data, required=False)
        policy_changed = "policy_id" in package_data
        policy = (
            ProductCommandService._get_package_policy(package_data.get("policy_id"))
            if policy_changed
            else package.policy
        )

        if items_data is not None or policy_changed:
            validation_items = items_data or [
                {
                    "drink_id": item.drink_id,
                    "quantity": item.quantity,
                    "sort_order": item.sort_order,
                }
                for item in package.items.all()
            ]
            ProductCommandService._validate_package_items(validation_items, policy)

        if package_data:
            update_fields = ["policy" if field == "policy_id" else field for field in package_data.keys()]
            update_fields.append("updated_at")
            for field, value in package_data.items():
                setattr(package, field, value)
            package.save(update_fields=update_fields)
        elif items_data is not None:
            package.save(update_fields=["updated_at"])

        if items_data is not None:
            ProductCommandService._replace_package_items(package, items_data)

    @staticmethod
    def _replace_package_items(package: Package, items_data: list[dict[str, Any]]) -> None:
        PackageItem.objects.filter(package=package).delete()
        ProductCommandService._create_package_items(package, items_data)

    @staticmethod
    def _create_package_items(package: Package, items_data: list[dict[str, Any]]) -> None:
        drink_ids = [item["drink_id"] for item in items_data]
        drinks_by_id = ProductCommandService._get_drinks_by_id(drink_ids)
        PackageItem.objects.bulk_create(
            [
                PackageItem(
                    package=package,
                    drink=drinks_by_id[item["drink_id"]],
                    quantity=item.get("quantity", 1),
                    sort_order=item.get("sort_order", index),
                )
                for index, item in enumerate(items_data)
            ]
        )

    @staticmethod
    def _normalize_package_items(package_data: dict[str, Any], *, required: bool = True) -> list[dict[str, Any]] | None:
        items_data = package_data.pop("items", None)
        drink_ids = package_data.pop("drink_ids", None)

        if items_data is not None:
            return [dict(item) for item in items_data]
        if drink_ids is not None:
            return [
                {"drink_id": drink_id, "quantity": 1, "sort_order": index} for index, drink_id in enumerate(drink_ids)
            ]
        if required:
            raise ValueError("패키지 구성 정보가 필요합니다.")
        return None

    @staticmethod
    def _get_package_policy(policy_id: int | None) -> PackagePolicy | None:
        if policy_id is None:
            return None
        try:
            return PackagePolicy.objects.get(id=policy_id, status=PackagePolicy.Status.ACTIVE)
        except PackagePolicy.DoesNotExist as exc:
            raise ValueError("존재하지 않거나 비활성 상태인 패키지 정책입니다.") from exc

    @staticmethod
    def _validate_package_items(items_data: list[dict[str, Any]], policy: PackagePolicy | None) -> None:
        for item in items_data:
            if not isinstance(item.get("drink_id"), int):
                raise ValueError("drink_id는 정수여야 합니다.")
            if not isinstance(item.get("quantity", 1), int) or item.get("quantity", 1) < 1:
                raise ValueError("quantity는 1 이상의 정수여야 합니다.")
            if not isinstance(item.get("sort_order", 0), int) or item.get("sort_order", 0) < 0:
                raise ValueError("sort_order는 0 이상의 정수여야 합니다.")

        total_quantity = sum(item.get("quantity", 1) for item in items_data)
        drink_ids = [item["drink_id"] for item in items_data]
        ProductCommandService._get_drinks_by_id(drink_ids)

        if len(drink_ids) != len(set(drink_ids)):
            raise ValueError("같은 술은 중복 row 대신 quantity로 표현해야 합니다.")

        if not policy:
            if not 2 <= total_quantity <= 5:
                raise ValueError("패키지 총 구성 수량은 2~5개여야 합니다.")
            if any(item.get("quantity", 1) > 1 for item in items_data):
                raise ValueError("중복 수량은 패키지 정책이 있을 때만 사용할 수 있습니다.")
            return

        if not policy.min_items <= total_quantity <= policy.max_items:
            raise ValueError(f"패키지 총 구성 수량은 {policy.min_items}~{policy.max_items}개여야 합니다.")
        if not policy.allow_duplicate_items and any(item.get("quantity", 1) > 1 for item in items_data):
            raise ValueError("이 패키지 정책은 같은 술 중복 구성을 허용하지 않습니다.")

        ProductCommandService._validate_package_policy_scope(policy, drink_ids)

    @staticmethod
    def _validate_package_policy_scope(policy: PackagePolicy, drink_ids: list[int]) -> None:
        if policy.allowed_item_scope == PackagePolicy.AllowedItemScope.PACKAGE_PRODUCTS:
            raise ValueError("현재 고정 패키지 구성은 단일 술 상품만 지원합니다.")
        if policy.allowed_item_scope != PackagePolicy.AllowedItemScope.ALLOWED_SET:
            return

        products_by_drink = Product.objects.filter(drink_id__in=drink_ids).in_bulk(field_name="drink_id")
        if len(products_by_drink) != len(set(drink_ids)):
            raise ValueError("정책 검증 가능한 상품이 없는 술이 포함되어 있습니다.")

        selected_product_ids = {product.id for product in products_by_drink.values()}
        allowed_product_ids = set(policy.allowed_products.values_list("id", flat=True))
        if not selected_product_ids.issubset(allowed_product_ids):
            raise ValueError("패키지 정책에서 허용하지 않은 상품이 포함되어 있습니다.")

    @staticmethod
    def _get_drinks_by_id(drink_ids: list[int]) -> dict[int, Drink]:
        drinks_by_id = Drink.objects.in_bulk(drink_ids)
        if len(drinks_by_id) != len(set(drink_ids)):
            raise ValueError("존재하지 않는 술이 포함되어 있습니다.")
        return drinks_by_id
