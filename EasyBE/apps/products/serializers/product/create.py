from rest_framework import serializers

from apps.products.services import ProductCommandService

from ..drink import DrinkCreateSerializer
from ..package import PackageCreateSerializer
from .detail import ProductDetailSerializer
from .image import ProductImageCreateSerializer, validate_product_images


class ProductBaseCreateSerializer(serializers.Serializer):
    """상품 생성 기본 시리얼라이저"""

    # 가격 정보
    price = serializers.IntegerField(min_value=0)
    original_price = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    discount = serializers.IntegerField(min_value=0, required=False, allow_null=True)

    # 상품 설명
    description = serializers.CharField()
    description_image_url = serializers.URLField()

    tag_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False, allow_empty=True)
    is_tasting_available = serializers.BooleanField(default=False)

    # 이미지
    images = ProductImageCreateSerializer(many=True)

    def validate(self, attrs):
        """공통 유효성 검사"""
        original_price = attrs.get("original_price")
        discount = attrs.get("discount")

        # 할인이 있다면 정가도 있어야 함
        if discount and not original_price:
            raise serializers.ValidationError({"original_price": "할인이 있을 경우 정가는 필수입니다."})

        # 할인금액이 정가보다 클 수 없음
        if original_price and discount and discount > original_price:
            raise serializers.ValidationError({"discount": "할인금액이 정가보다 클 수 없습니다."})

        return attrs

    def validate_tag_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("상품 태그는 중복될 수 없습니다.")
        return value

    def validate_images(self, value):
        """이미지 유효성 검사"""
        return validate_product_images(value)


class IndividualProductCreateSerializer(ProductBaseCreateSerializer):
    """개별 상품 생성용 시리얼라이저"""

    drink_info = DrinkCreateSerializer()

    def create(self, validated_data):
        """개별 상품 생성."""
        drink_data = validated_data.pop("drink_info")
        images_data = validated_data.pop("images")
        tag_ids = validated_data.pop("tag_ids", [])
        try:
            return ProductCommandService.create_single_product(
                drink_data=drink_data,
                product_data=validated_data,
                images_data=images_data,
                tag_ids=tag_ids,
            )
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

    def to_representation(self, instance):
        """응답 시리얼라이저"""
        return ProductDetailSerializer(instance).data


class PackageProductCreateSerializer(ProductBaseCreateSerializer):
    """패키지 상품 생성용 시리얼라이저"""

    package_info = PackageCreateSerializer()

    def create(self, validated_data):
        """패키지 상품 생성."""
        package_data = validated_data.pop("package_info")
        images_data = validated_data.pop("images")
        tag_ids = validated_data.pop("tag_ids", [])
        try:
            return ProductCommandService.create_package_product(
                package_data=package_data,
                product_data=validated_data,
                images_data=images_data,
                tag_ids=tag_ids,
            )
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

    def to_representation(self, instance):
        """응답 시리얼라이저"""
        return ProductDetailSerializer(instance).data
