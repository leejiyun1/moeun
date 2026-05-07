from dataclasses import dataclass
from typing import Iterable, Optional

from apps.products.models import Drink, Product
from apps.products.selectors import ProductSelector
from apps.users.models import PreferTasteProfile, User

TASTE_FIELDS = (
    "sweetness_level",
    "acidity_level",
    "body_level",
    "carbonation_level",
    "bitterness_level",
    "aroma_level",
)


@dataclass(frozen=True)
class RecommendationResult:
    title: str
    mode: str
    products: list[Product]


class ProductRecommendationService:
    """상품 추천 전용 서비스.

    검색/섹션 조회와 분리해서 추천 후보, 점수, fallback 기준을 한 곳에서 관리한다.
    """

    PERSONALIZED_MODE = "personalized"
    FALLBACK_MODE = "fallback"

    @classmethod
    def get_recommendations(cls, user: Optional[User], limit: int = 8) -> RecommendationResult:
        profile = cls._get_profile(user)
        candidates = list(ProductSelector.with_user_like_status(cls._candidate_queryset(), user))

        if profile:
            products = cls._rank_personalized(candidates, profile)[:limit]
            return RecommendationResult(title="취향 기반 추천 전통주", mode=cls.PERSONALIZED_MODE, products=products)

        products = cls._rank_fallback(candidates)[:limit]
        return RecommendationResult(title="추천 전통주", mode=cls.FALLBACK_MODE, products=products)

    @staticmethod
    def _candidate_queryset():
        return ProductSelector.active_queryset().order_by("-created_at")

    @staticmethod
    def _get_profile(user: Optional[User]) -> Optional[PreferTasteProfile]:
        if not user or not getattr(user, "is_authenticated", False):
            return None

        try:
            return user.taste_profile
        except PreferTasteProfile.DoesNotExist:
            return None

    @classmethod
    def _rank_personalized(cls, products: Iterable[Product], profile: PreferTasteProfile) -> list[Product]:
        profile_vector = cls._profile_vector(profile)
        scored_products = []

        for product in products:
            taste_vector = cls._product_taste_vector(product)
            if not taste_vector:
                continue

            taste_score = cls._taste_similarity(profile_vector, taste_vector) * 70
            engagement_score = cls._engagement_score(product) * 20
            operation_score = cls._operation_score(product) * 10
            final_score = round(taste_score + engagement_score + operation_score, 2)
            cls._attach_recommendation(product, final_score, cls._build_reason(profile_vector, taste_vector))
            scored_products.append(product)

        return sorted(scored_products, key=cls._sort_key, reverse=True)

    @classmethod
    def _rank_fallback(cls, products: Iterable[Product]) -> list[Product]:
        scored_products = []
        products_by_recency = sorted(products, key=lambda product: product.created_at, reverse=True)
        max_index = max(len(products_by_recency) - 1, 1)

        for index, product in enumerate(products_by_recency):
            engagement_score = cls._engagement_score(product) * 65
            operation_score = cls._operation_score(product) * 25
            recency_score = (1 - (index / max_index)) * 10
            final_score = round(engagement_score + operation_score + recency_score, 2)
            cls._attach_recommendation(product, final_score, "인기와 운영 추천 기준을 함께 반영한 상품입니다.")
            scored_products.append(product)

        return sorted(scored_products, key=cls._sort_key, reverse=True)

    @staticmethod
    def _profile_vector(profile: PreferTasteProfile) -> dict[str, float]:
        return {field: float(getattr(profile, field)) for field in TASTE_FIELDS}

    @classmethod
    def _product_taste_vector(cls, product: Product) -> Optional[dict[str, float]]:
        if product.drink:
            return cls._drink_vector(product.drink)

        if not product.package:
            return None

        items = list(product.package.items.all())
        if not items:
            return None

        total_quantity = sum(item.quantity for item in items)
        if total_quantity <= 0:
            return None

        vector = {field: 0.0 for field in TASTE_FIELDS}
        for item in items:
            drink_vector = cls._drink_vector(item.drink)
            for field in TASTE_FIELDS:
                vector[field] += drink_vector[field] * item.quantity

        return {field: value / total_quantity for field, value in vector.items()}

    @staticmethod
    def _drink_vector(drink: Drink) -> dict[str, float]:
        return {field: float(getattr(drink, field)) for field in TASTE_FIELDS}

    @staticmethod
    def _taste_similarity(profile_vector: dict[str, float], taste_vector: dict[str, float]) -> float:
        total_distance = sum(abs(profile_vector[field] - taste_vector[field]) for field in TASTE_FIELDS)
        average_distance = total_distance / len(TASTE_FIELDS)
        return max(0.0, 1 - (average_distance / 5))

    @staticmethod
    def _engagement_score(product: Product) -> float:
        weighted_score = (
            product.view_count * 0.05
            + product.like_count * 0.2
            + product.order_count * 0.35
            + product.review_count * 0.25
        )
        return min(weighted_score, 1.0)

    @staticmethod
    def _operation_score(product: Product) -> float:
        product_tag_slugs = {tag.slug for tag in product.tags.all() if tag.is_active}
        enabled_flags = sum(
            [
                "premium" in product_tag_slugs,
                "award-winning" in product_tag_slugs,
                "regional-specialty" in product_tag_slugs,
                "gift-suitable" in product_tag_slugs,
                product.is_tasting_available,
            ]
        )
        return min(enabled_flags / 5, 1.0)

    @staticmethod
    def _attach_recommendation(product: Product, score: float, reason: str) -> None:
        product.recommendation_score = score
        product.recommendation_reason = reason

    @staticmethod
    def _build_reason(profile_vector: dict[str, float], taste_vector: dict[str, float]) -> str:
        closest_field = min(TASTE_FIELDS, key=lambda field: abs(profile_vector[field] - taste_vector[field]))
        labels = {
            "sweetness_level": "단맛",
            "acidity_level": "산미",
            "body_level": "바디감",
            "carbonation_level": "탄산감",
            "bitterness_level": "쓴맛",
            "aroma_level": "향",
        }
        return f"{labels[closest_field]} 선호도에 잘 맞는 상품입니다."

    @staticmethod
    def _sort_key(product: Product):
        return (
            getattr(product, "recommendation_score", 0),
            product.order_count,
            product.like_count,
            product.view_count,
            product.created_at,
        )
