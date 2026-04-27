from rest_framework import serializers

from apps.products.models import Product
from apps.stores.models import Store
from apps.stores.serializers import StoreSerializer

from .models import CartItem, PackageDraft, PackageDraftItem
from .services import (
    CartPackageDraftService,
    CartService,
    CartValidationError,
    PackageDraftValidationError,
)


class _CartProductSerializer(serializers.ModelSerializer):
    """
    장바구니 내부에 표시될 상품 정보를 위한 내부 시리얼라이저.
    Product가 drink인지 package인지에 따라 이름과 이미지를 가져옵니다.
    """

    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "price", "main_image"]

    def get_main_image(self, obj):
        """상품의 메인 이미지를 반환합니다."""
        for image in obj.images.all():
            if image.is_main:
                return image.image_url
        return None


class CartItemSerializer(serializers.ModelSerializer):
    """
    장바구니 항목 CRUD를 위한 메인 시리얼라이저.
    비즈니스 로직은 CartService에 위임합니다.
    """

    product = _CartProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    quantity = serializers.IntegerField(min_value=0)
    subtotal = serializers.SerializerMethodField()

    pickup_store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        write_only=True,
        source="pickup_store",
        required=False,
        allow_null=True,
    )
    pickup_date = serializers.DateField(required=False, allow_null=True)

    # READ-ONLY fields for displaying cart items
    pickup_store_name = serializers.CharField(source="pickup_store.name", read_only=True)
    pickup_store_contact = serializers.CharField(source="pickup_store.contact", read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "subtotal",
            "pickup_store_id",
            "pickup_date",
            "pickup_store_name",
            "pickup_store_contact",
        ]
        read_only_fields = [
            "id",
            "product",
            "subtotal",
            "pickup_store_name",
            "pickup_store_contact",
        ]

    def get_subtotal(self, obj):
        """항목별 소계 (가격 * 수량)를 계산합니다."""
        return obj.product.price * obj.quantity

    def create(self, validated_data):
        user = self.context["request"].user
        product_id = validated_data.pop("product_id")
        pickup_store = validated_data.pop("pickup_store", None)

        try:
            return CartService.add_or_update_item(
                user=user, product_id=product_id, pickup_store=pickup_store, **validated_data
            )
        except CartValidationError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

    def update(self, instance, validated_data):
        try:
            return CartService.update_item(cart_item=instance, data=validated_data)
        except CartValidationError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc


class PackageDraftItemRequestSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    sort_order = serializers.IntegerField(min_value=0, required=False)


class PackageDraftItemSerializer(serializers.ModelSerializer):
    product = _CartProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = PackageDraftItem
        fields = ["id", "product", "quantity", "sort_order", "subtotal"]

    def get_subtotal(self, obj):
        return obj.total_price


class PackageDraftSerializer(serializers.ModelSerializer):
    policy_id = serializers.IntegerField(write_only=True, required=False)
    items = PackageDraftItemSerializer(many=True, read_only=True)
    item_inputs = PackageDraftItemRequestSerializer(many=True, write_only=True, source="items", required=False)
    pickup_store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        write_only=True,
        source="pickup_store",
        required=False,
        allow_null=True,
    )
    pickup_store = StoreSerializer(read_only=True)

    class Meta:
        model = PackageDraft
        fields = [
            "id",
            "policy",
            "policy_id",
            "display_name",
            "items",
            "item_inputs",
            "base_price",
            "discount_amount",
            "final_price",
            "status",
            "pickup_store_id",
            "pickup_store",
            "pickup_date",
            "is_tasting_selected",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "policy",
            "items",
            "base_price",
            "discount_amount",
            "final_price",
            "status",
            "pickup_store",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        if self.instance is None and "policy_id" not in attrs:
            raise serializers.ValidationError({"policy_id": "패키지 정책은 필수입니다."})
        if self.instance is None and "items" not in attrs:
            raise serializers.ValidationError({"item_inputs": "패키지 구성은 필수입니다."})
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        items = validated_data.pop("items")
        try:
            return CartPackageDraftService.create_draft(user=user, items=items, **validated_data)
        except PackageDraftValidationError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

    def update(self, instance, validated_data):
        try:
            return CartPackageDraftService.update_draft(instance, validated_data)
        except PackageDraftValidationError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc
