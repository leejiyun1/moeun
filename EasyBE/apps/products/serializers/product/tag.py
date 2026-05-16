from rest_framework import serializers

from apps.products.models import ProductTag


class ProductTagSerializer(serializers.ModelSerializer):
    """상품 태그 응답 serializer."""

    class Meta:
        model = ProductTag
        fields = ["id", "name", "group", "description", "is_active", "sort_order"]


class ProductTagManageSerializer(serializers.ModelSerializer):
    """관리자용 상품 태그 serializer."""

    class Meta:
        model = ProductTag
        fields = [
            "id",
            "name",
            "group",
            "description",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
