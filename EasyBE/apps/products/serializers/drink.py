# apps/products/serializers/drink.py

from typing import Optional

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.products.models import Drink, Product

from .brewery import BrewerySimpleSerializer


class DrinkCreateSerializer(serializers.ModelSerializer):
    """술 생성용 시리얼라이저"""

    brewery_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Drink
        fields = [
            "name",
            "brewery_id",
            "ingredients",
            "alcohol_type",
            "abv",
            "volume_ml",
            "sweetness_level",
            "acidity_level",
            "body_level",
            "carbonation_level",
            "bitterness_level",
            "aroma_level",
        ]

    def validate_brewery_id(self, value):
        """양조장 존재 여부 확인"""
        from apps.products.models import Brewery

        if not Brewery.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("존재하지 않거나 비활성 상태인 양조장입니다.")
        return value

    def validate_name(self, value):
        """술 이름 유효성 검사"""
        if not value or not value.strip():
            raise serializers.ValidationError("술 이름은 필수입니다.")
        return value.strip()

    def validate(self, attrs):
        """전체 유효성 검사 - 중복 이름 체크"""
        brewery_id = attrs.get("brewery_id")
        name = attrs.get("name")

        # 같은 양조장에서 동일한 이름의 술이 있는지 확인
        if Drink.objects.filter(brewery_id=brewery_id, name=name).exists():
            raise serializers.ValidationError({"name": "같은 양조장에서 동일한 이름의 술이 이미 존재합니다."})

        return attrs


class DrinkUpdateSerializer(DrinkCreateSerializer):
    """술 수정용 request serializer."""

    brewery_id = serializers.IntegerField(required=False, write_only=True)

    def validate(self, attrs):
        """전체 유효성 검사 - 같은 양조장 내 중복 이름 체크."""
        brewery_id = attrs.get("brewery_id", getattr(self.instance, "brewery_id", None))
        name = attrs.get("name", getattr(self.instance, "name", None))

        if brewery_id and name:
            queryset = Drink.objects.filter(brewery_id=brewery_id, name=name)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"name": "같은 양조장에서 동일한 이름의 술이 이미 존재합니다."})

        return attrs


class DrinkListSerializer(serializers.ModelSerializer):
    """술 목록용 시리얼라이저 (관리자용 - 선택 목록)"""

    brewery = BrewerySimpleSerializer(read_only=True)
    alcohol_type_display = serializers.CharField(source="get_alcohol_type_display", read_only=True)

    class Meta:
        model = Drink
        fields = ["id", "name", "brewery", "alcohol_type", "alcohol_type_display", "abv", "volume_ml", "created_at"]


class DrinkForPackageSerializer(serializers.ModelSerializer):
    """패키지 생성용 술 목록 시리얼라이저"""

    brewery = BrewerySimpleSerializer(read_only=True)
    main_image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Drink
        fields = ["id", "name", "brewery", "alcohol_type", "abv", "main_image", "price"]

    def _get_product(self, obj) -> Optional[Product]:
        try:
            return obj.product
        except Product.DoesNotExist:
            return None

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_main_image(self, obj) -> Optional[str]:
        """술의 메인 이미지 URL 반환"""
        product = self._get_product(obj)
        if not product:
            return None

        for image in product.images.all():
            if image.is_main:
                return image.image_url
        return None

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_price(self, obj) -> Optional[int]:
        """술의 개별 상품 가격 반환"""
        product = self._get_product(obj)
        return product.price if product else None
