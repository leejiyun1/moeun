# apps/products/serializers/product/image.py

from rest_framework import serializers

from apps.products.models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """상품 이미지 시리얼라이저"""

    class Meta:
        model = ProductImage
        fields = ["image_url", "is_main", "created_at"]


class ProductImageCreateSerializer(serializers.ModelSerializer):
    """상품 이미지 생성용 시리얼라이저"""

    class Meta:
        model = ProductImage
        fields = ["image_url", "is_main"]

    def validate_image_url(self, value):
        """이미지 URL 유효성 검사"""
        if not value or not value.strip():
            raise serializers.ValidationError("이미지 URL은 필수입니다.")
        return value.strip()


def validate_product_images(value):
    """상품 이미지 목록 공통 검증."""
    if not value:
        raise serializers.ValidationError("최소 1개의 이미지는 필요합니다.")

    main_images = [image for image in value if image.get("is_main")]
    if len(main_images) != 1:
        raise serializers.ValidationError("메인 이미지는 정확히 1개여야 합니다.")

    if len(value) > 5:
        raise serializers.ValidationError("이미지는 최대 5개까지 업로드 가능합니다.")

    return value
