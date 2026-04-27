from decimal import Decimal, InvalidOperation
from typing import Dict

from django.db.models import QuerySet
from django.http import QueryDict
from django.shortcuts import get_object_or_404

from apps.products.models import Drink, PackagePolicy, Product


class ProductSelector:
    """상품 조회 전용 selector."""

    SECTION_MONTHLY = "monthly"
    SECTION_POPULAR = "popular"
    SECTION_RECOMMENDED = "recommended"
    SECTION_FEATURED = "featured"
    SECTION_AWARD_WINNING = "award_winning"
    SECTION_MAKGEOLLI = "makgeolli"
    SECTION_REGIONAL = "regional"

    TASTE_PARAM_MAPPING: Dict[str, str] = {
        "sweetness": "drink__sweetness_level",
        "acidity": "drink__acidity_level",
        "body": "drink__body_level",
        "carbonation": "drink__carbonation_level",
        "bitterness": "drink__bitterness_level",
        "aroma": "drink__aroma_level",
    }

    CATEGORY_FILTER_MAPPING: Dict[str, str] = {
        "gift_suitable": "is_gift_suitable",
        "regional_specialty": "is_regional_specialty",
        "limited_edition": "is_limited_edition",
        "premium": "is_premium",
        "award_winning": "is_award_winning",
    }

    TASTE_RANGE = Decimal("0.5")
    MIN_TASTE_VALUE = Decimal("0.0")
    MAX_TASTE_VALUE = Decimal("5.0")

    @staticmethod
    def base_queryset() -> QuerySet:
        return Product.objects.select_related("drink__brewery", "package", "package__policy").prefetch_related(
            "images",
            "package__drinks__brewery",
            "package__items__drink__brewery",
        )

    @staticmethod
    def active_queryset() -> QuerySet:
        return ProductSelector.base_queryset().filter(status=Product.Status.ACTIVE)

    @staticmethod
    def management_queryset() -> QuerySet:
        return ProductSelector.base_queryset()

    @staticmethod
    def get_active_product_or_404(product_id: str) -> Product:
        return get_object_or_404(ProductSelector.active_queryset(), pk=product_id)

    @staticmethod
    def get_management_product_or_404(product_id: str) -> Product:
        return get_object_or_404(ProductSelector.management_queryset(), pk=product_id)

    @staticmethod
    def get_management_list_queryset(status_filter: str | None = None) -> QuerySet:
        queryset = ProductSelector.management_queryset()
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    @staticmethod
    def get_drinks_for_package_queryset() -> QuerySet:
        return (
            Drink.objects.filter(product__isnull=False, product__status=Product.Status.ACTIVE)
            .select_related("brewery")
            .prefetch_related("product__images")
            .order_by("name")
        )

    @staticmethod
    def get_search_queryset(query_params: QueryDict) -> QuerySet:
        queryset = ProductSelector.active_queryset()
        queryset = ProductSelector.apply_taste_filters(queryset, query_params)
        return ProductSelector.apply_category_filters(queryset, query_params)

    @staticmethod
    def apply_taste_filters(queryset: QuerySet, query_params: QueryDict) -> QuerySet:
        for param, field in ProductSelector.TASTE_PARAM_MAPPING.items():
            value = query_params.get(param)
            if not value:
                continue

            try:
                target = Decimal(str(value))
            except (TypeError, ValueError, InvalidOperation):
                continue

            min_value = max(ProductSelector.MIN_TASTE_VALUE, target - ProductSelector.TASTE_RANGE)
            max_value = min(ProductSelector.MAX_TASTE_VALUE, target + ProductSelector.TASTE_RANGE)
            queryset = queryset.filter(
                **{f"{field}__gte": min_value},
                **{f"{field}__lte": max_value},
            )

        return queryset

    @staticmethod
    def apply_category_filters(queryset: QuerySet, query_params: QueryDict) -> QuerySet:
        for param, field in ProductSelector.CATEGORY_FILTER_MAPPING.items():
            if query_params.get(param) == "true":
                queryset = queryset.filter(**{field: True})
        return queryset

    @staticmethod
    def get_section_products(section_type: str, limit: int = 8) -> QuerySet:
        queryset = ProductSelector.active_queryset()

        if section_type == ProductSelector.SECTION_POPULAR:
            queryset = queryset.filter(package__isnull=False).order_by("-view_count")
        elif section_type == ProductSelector.SECTION_FEATURED:
            queryset = queryset.filter(package__isnull=False).order_by("-created_at")
        elif section_type == ProductSelector.SECTION_RECOMMENDED:
            queryset = queryset.filter(drink__isnull=False).order_by("-created_at")
        elif section_type == ProductSelector.SECTION_MONTHLY:
            queryset = queryset.filter(drink__isnull=False).order_by("-view_count")
            limit = 3
        elif section_type == ProductSelector.SECTION_AWARD_WINNING:
            queryset = queryset.filter(is_award_winning=True, package__isnull=False).order_by("-order_count")
        elif section_type == ProductSelector.SECTION_MAKGEOLLI:
            queryset = queryset.filter(package__isnull=False, package__name__icontains="막걸리").order_by("-created_at")
        elif section_type == ProductSelector.SECTION_REGIONAL:
            queryset = queryset.filter(is_regional_specialty=True, package__isnull=False).order_by("-created_at")
        else:
            return queryset.none()

        return queryset[:limit]


class PackagePolicySelector:
    """패키지 정책 조회 전용 selector."""

    @staticmethod
    def management_queryset() -> QuerySet:
        return PackagePolicy.objects.prefetch_related(
            "allowed_products__images",
            "allowed_products__drink",
            "allowed_products__package",
        ).order_by("-created_at")
