from rest_framework import serializers

from apps.products.models import PackagePolicy, Product
from apps.products.services import PackagePolicyCommandService


class PackagePolicyAllowedProductSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "price", "status", "main_image"]

    def get_main_image(self, obj):
        for image in obj.images.all():
            if image.is_main:
                return image.image_url
        return None


class PackagePolicySerializer(serializers.ModelSerializer):
    allowed_product_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    allowed_products = PackagePolicyAllowedProductSerializer(many=True, read_only=True)

    class Meta:
        model = PackagePolicy
        fields = [
            "id",
            "name",
            "status",
            "min_items",
            "max_items",
            "allow_duplicate_items",
            "allowed_item_scope",
            "discount_type",
            "discount_value",
            "allowed_product_ids",
            "allowed_products",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "allowed_products", "created_at", "updated_at"]

    def validate(self, attrs):
        min_items = attrs.get("min_items", getattr(self.instance, "min_items", None))
        max_items = attrs.get("max_items", getattr(self.instance, "max_items", None))
        discount_type = attrs.get("discount_type", getattr(self.instance, "discount_type", None))
        discount_value = attrs.get("discount_value", getattr(self.instance, "discount_value", 0))
        allowed_item_scope = attrs.get("allowed_item_scope", getattr(self.instance, "allowed_item_scope", None))
        allowed_product_ids = attrs.get("allowed_product_ids")

        if min_items is not None and max_items is not None and min_items > max_items:
            raise serializers.ValidationError({"min_items": "최소 구성 수량은 최대 구성 수량보다 클 수 없습니다."})
        if discount_type == PackagePolicy.DiscountType.NONE and discount_value:
            raise serializers.ValidationError(
                {"discount_value": "할인 없음 정책에서는 할인 금액을 설정할 수 없습니다."}
            )
        if allowed_product_ids is not None and len(allowed_product_ids) != len(set(allowed_product_ids)):
            raise serializers.ValidationError({"allowed_product_ids": "허용 상품 ID는 중복될 수 없습니다."})
        if allowed_item_scope == PackagePolicy.AllowedItemScope.ALLOWED_SET:
            has_existing_allowed_products = self.instance is not None and self.instance.allowed_products.exists()
            if allowed_product_ids is None and not has_existing_allowed_products:
                raise serializers.ValidationError(
                    {"allowed_product_ids": "허용 상품만 정책은 허용 상품 목록이 필요합니다."}
                )
            if allowed_product_ids == []:
                raise serializers.ValidationError(
                    {"allowed_product_ids": "허용 상품만 정책은 최소 1개 이상의 상품이 필요합니다."}
                )

        return attrs

    def create(self, validated_data):
        allowed_product_ids = [str(product_id) for product_id in validated_data.pop("allowed_product_ids", [])]
        try:
            return PackagePolicyCommandService.create_policy(validated_data, allowed_product_ids)
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

    def update(self, instance, validated_data):
        allowed_product_ids = validated_data.pop("allowed_product_ids", None)
        if allowed_product_ids is not None:
            allowed_product_ids = [str(product_id) for product_id in allowed_product_ids]

        try:
            return PackagePolicyCommandService.update_policy(instance, validated_data, allowed_product_ids)
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc
