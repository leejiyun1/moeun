from rest_framework import serializers

from apps.products.models import Product
from apps.products.serializers.drink import DrinkUpdateSerializer
from apps.products.serializers.package import PackageUpdateSerializer

from .image import ProductImageCreateSerializer, validate_product_images


class ProductUpdateSerializer(serializers.Serializer):
    """상품 공통 판매 정보 수정용 request serializer."""

    price = serializers.IntegerField(min_value=0, required=False)
    original_price = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    discount = serializers.IntegerField(min_value=0, required=False, allow_null=True)

    description = serializers.CharField(required=False)
    description_image_url = serializers.URLField(required=False)

    is_gift_suitable = serializers.BooleanField(required=False)
    is_award_winning = serializers.BooleanField(required=False)
    is_regional_specialty = serializers.BooleanField(required=False)
    is_limited_edition = serializers.BooleanField(required=False)
    is_premium = serializers.BooleanField(required=False)
    is_organic = serializers.BooleanField(required=False)
    status = serializers.ChoiceField(choices=Product.Status.choices, required=False)
    images = ProductImageCreateSerializer(many=True, required=False)
    drink_info = serializers.DictField(required=False)
    package_info = serializers.DictField(required=False)

    def validate(self, attrs):
        original_price = attrs.get("original_price", getattr(self.instance, "original_price", None))
        discount = attrs.get("discount", getattr(self.instance, "discount", None))

        if discount and not original_price:
            raise serializers.ValidationError({"original_price": "할인이 있을 경우 정가는 필수입니다."})

        if original_price and discount and discount > original_price:
            raise serializers.ValidationError({"discount": "할인금액이 정가보다 클 수 없습니다."})

        self._validate_nested_payloads(attrs)
        return attrs

    def validate_images(self, value):
        return validate_product_images(value)

    def _validate_nested_payloads(self, attrs):
        if "drink_info" in attrs:
            if not self.instance or not self.instance.drink_id:
                raise serializers.ValidationError({"drink_info": "개별 술 상품에서만 수정할 수 있습니다."})
            serializer = DrinkUpdateSerializer(instance=self.instance.drink, data=attrs["drink_info"], partial=True)
            serializer.is_valid(raise_exception=True)
            attrs["drink_info"] = serializer.validated_data

        if "package_info" in attrs:
            if not self.instance or not self.instance.package_id:
                raise serializers.ValidationError({"package_info": "패키지 상품에서만 수정할 수 있습니다."})
            serializer = PackageUpdateSerializer(
                instance=self.instance.package,
                data=attrs["package_info"],
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            attrs["package_info"] = serializer.validated_data
