from typing import Any

from django.db import transaction

from apps.products.models import PackagePolicy, Product


class PackagePolicyCommandService:
    """패키지 정책 생성/수정/비활성화 write 오케스트레이션."""

    @staticmethod
    @transaction.atomic
    def create_policy(policy_data: dict[str, Any], allowed_product_ids: list[str] | None = None) -> PackagePolicy:
        policy = PackagePolicy.objects.create(**dict(policy_data))
        PackagePolicyCommandService._replace_allowed_products(policy, allowed_product_ids)
        return policy

    @staticmethod
    @transaction.atomic
    def update_policy(
        policy: PackagePolicy,
        policy_data: dict[str, Any],
        allowed_product_ids: list[str] | None = None,
    ) -> PackagePolicy:
        if policy_data:
            update_fields = [*policy_data.keys(), "updated_at"]
            for field, value in policy_data.items():
                setattr(policy, field, value)
            policy.save(update_fields=update_fields)

        if allowed_product_ids is not None:
            PackagePolicyCommandService._replace_allowed_products(policy, allowed_product_ids)

        return policy

    @staticmethod
    @transaction.atomic
    def deactivate_policy(policy: PackagePolicy) -> PackagePolicy:
        policy.status = PackagePolicy.Status.INACTIVE
        policy.save(update_fields=["status", "updated_at"])
        return policy

    @staticmethod
    def _replace_allowed_products(policy: PackagePolicy, allowed_product_ids: list[str] | None) -> None:
        if allowed_product_ids is None:
            return

        products = Product.objects.filter(id__in=allowed_product_ids, status=Product.Status.ACTIVE)
        products_by_id = {str(product.id): product for product in products}
        if len(products_by_id) != len(set(allowed_product_ids)):
            raise ValueError("존재하지 않거나 비활성 상태인 상품이 허용 목록에 포함되어 있습니다.")

        policy.allowed_products.set(products_by_id.values())
