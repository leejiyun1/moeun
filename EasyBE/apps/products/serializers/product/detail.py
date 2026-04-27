from rest_framework import serializers

from apps.products.models import Drink, Package, PackageItem, PackagePolicy, Product

from ..brewery import BrewerySimpleSerializer
from .image import ProductImageSerializer


class DrinkTasteProfileSerializer(serializers.Serializer):
    """술 맛 프로필 응답 serializer."""

    sweetness = serializers.FloatField(source="sweetness_level", read_only=True)
    acidity = serializers.FloatField(source="acidity_level", read_only=True)
    body = serializers.FloatField(source="body_level", read_only=True)
    carbonation = serializers.FloatField(source="carbonation_level", read_only=True)
    bitterness = serializers.FloatField(source="bitterness_level", read_only=True)
    aroma = serializers.FloatField(source="aroma_level", read_only=True)


class ProductDrinkSerializer(serializers.ModelSerializer):
    """상품 상세용 술 serializer."""

    brewery = BrewerySimpleSerializer(read_only=True)
    alcohol_type_display = serializers.CharField(source="get_alcohol_type_display", read_only=True)
    abv = serializers.FloatField(read_only=True)
    taste_profile = DrinkTasteProfileSerializer(source="*", read_only=True)

    class Meta:
        model = Drink
        fields = [
            "id",
            "name",
            "brewery",
            "ingredients",
            "alcohol_type",
            "alcohol_type_display",
            "abv",
            "volume_ml",
            "taste_profile",
            "created_at",
            "updated_at",
        ]


class PackageDrinkSerializer(serializers.ModelSerializer):
    """패키지 내부 술 serializer."""

    brewery = BrewerySimpleSerializer(read_only=True)
    alcohol_type_display = serializers.CharField(source="get_alcohol_type_display", read_only=True)
    abv = serializers.FloatField(read_only=True)

    class Meta:
        model = Drink
        fields = [
            "id",
            "name",
            "brewery",
            "alcohol_type",
            "alcohol_type_display",
            "abv",
            "volume_ml",
        ]


class PackagePolicySummarySerializer(serializers.ModelSerializer):
    """상품 상세용 패키지 정책 요약 serializer."""

    class Meta:
        model = PackagePolicy
        fields = [
            "id",
            "name",
            "min_items",
            "max_items",
            "allow_duplicate_items",
            "allowed_item_scope",
            "discount_type",
            "discount_value",
        ]


class ProductPackageItemSerializer(serializers.ModelSerializer):
    """상품 상세용 패키지 구성 serializer."""

    drink = PackageDrinkSerializer(read_only=True)

    class Meta:
        model = PackageItem
        fields = [
            "id",
            "drink",
            "quantity",
            "sort_order",
        ]


class ProductPackageSerializer(serializers.ModelSerializer):
    """상품 상세용 패키지 serializer."""

    type_display = serializers.CharField(source="get_type_display", read_only=True)
    policy = PackagePolicySummarySerializer(read_only=True)
    drinks = PackageDrinkSerializer(many=True, read_only=True)
    items = ProductPackageItemSerializer(many=True, read_only=True)
    drink_count = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = [
            "id",
            "name",
            "type",
            "type_display",
            "policy",
            "drinks",
            "items",
            "drink_count",
            "created_at",
            "updated_at",
        ]

    def get_drink_count(self, obj) -> int:
        items = list(obj.items.all())
        if items:
            return sum(item.quantity for item in items)
        return len(obj.drinks.all())


class ProductDetailSerializer(serializers.ModelSerializer):
    """상품 상세 시리얼라이저"""

    name = serializers.ReadOnlyField()
    product_type = serializers.ReadOnlyField()

    drink = ProductDrinkSerializer(read_only=True)
    package = ProductPackageSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    # 할인 정보
    discount_rate = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_type",
            "drink",
            "package",
            "price",
            "original_price",
            "discount",
            "discount_rate",
            "final_price",
            "is_on_sale",
            "description",
            "description_image_url",
            "is_gift_suitable",
            "is_award_winning",
            "is_regional_specialty",
            "is_limited_edition",
            "is_premium",
            "is_organic",
            "view_count",
            "order_count",
            "like_count",
            "review_count",
            "status",
            "images",
            "created_at",
            "updated_at",
        ]

    def get_discount_rate(self, obj) -> float:
        return obj.get_discount_rate()

    def get_final_price(self, obj) -> int:
        return obj.get_final_price()

    def get_is_on_sale(self, obj) -> bool:
        return obj.is_on_sale()
