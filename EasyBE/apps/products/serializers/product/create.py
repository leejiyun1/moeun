import json

from django.http import QueryDict
from rest_framework import serializers

from apps.products.services import ProductCommandService
from apps.products.services.product_image_storage import ProductImageStorage

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
    description_image_url = serializers.URLField(required=False)
    description_image_file = serializers.FileField(write_only=True, required=False)

    tag_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False, allow_empty=True)
    is_tasting_available = serializers.BooleanField(default=False)

    # 이미지
    images = ProductImageCreateSerializer(many=True, required=False)
    main_image_file = serializers.FileField(write_only=True, required=False)

    json_fields: tuple[str, ...] = ("tag_ids",)

    def to_internal_value(self, data):
        return super().to_internal_value(self._normalize_multipart_data(data))

    def _normalize_multipart_data(self, data):
        if not isinstance(data, QueryDict):
            return data

        normalized = {key: data.get(key) for key in data.keys()}
        for field in self.json_fields:
            value = normalized.get(field)
            if isinstance(value, str) and value:
                try:
                    normalized[field] = json.loads(value)
                except json.JSONDecodeError as exc:
                    raise serializers.ValidationError({field: "올바른 JSON 형식이 아닙니다."}) from exc
        return normalized

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

        has_description_image = bool(attrs.get("description_image_url") or attrs.get("description_image_file"))
        if not has_description_image:
            raise serializers.ValidationError({"description_image_file": "상세 설명 이미지는 필수입니다."})

        return attrs

    def validate_tag_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("상품 태그는 중복될 수 없습니다.")
        return value

    def validate_images(self, value):
        """이미지 유효성 검사"""
        return validate_product_images(value)

    def _prepare_product_payload(self, validated_data):
        description_image_file = validated_data.pop("description_image_file", None)
        main_image_file = validated_data.pop("main_image_file", None)
        images_data = validated_data.pop("images", None)

        try:
            if description_image_file:
                validated_data["description_image_url"] = ProductImageStorage.save_description_image(
                    description_image_file
                )
            if main_image_file:
                images_data = [
                    {
                        "image_url": ProductImageStorage.save_main_image(main_image_file),
                        "is_main": True,
                    }
                ]
        except ValueError as exc:
            raise serializers.ValidationError({"images": str(exc)}) from exc

        if images_data is None:
            raise serializers.ValidationError({"main_image_file": "대표 이미지는 필수입니다."})

        images_data = validate_product_images(images_data)
        return validated_data, images_data


class IndividualProductCreateSerializer(ProductBaseCreateSerializer):
    """개별 상품 생성용 시리얼라이저"""

    drink_info = DrinkCreateSerializer()
    json_fields = (*ProductBaseCreateSerializer.json_fields, "drink_info")

    def create(self, validated_data):
        """개별 상품 생성."""
        drink_data = validated_data.pop("drink_info")
        validated_data, images_data = self._prepare_product_payload(validated_data)
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
    json_fields = (*ProductBaseCreateSerializer.json_fields, "package_info")

    def create(self, validated_data):
        """패키지 상품 생성."""
        package_data = validated_data.pop("package_info")
        validated_data, images_data = self._prepare_product_payload(validated_data)
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
