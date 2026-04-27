from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CartItem
from .serializers import CartItemSerializer, PackageDraftSerializer
from .services import CartPackageDraftService, CartService


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """현재 인증된 사용자의 장바구니 항목만 조회하도록 필터링합니다."""
        return (
            CartItem.objects.filter(user=self.request.user)
            .select_related("product", "pickup_store")
            .prefetch_related("product__images", "product__drink", "product__package")
        )

    def get_serializer_context(self):
        """시리얼라이저에 request 객체를 전달합니다."""
        return {"request": self.request}

    def list(self, request, *args, **kwargs):
        """
        사용자의 장바구니에 담긴 모든 항목과 총액을 조회합니다.
        """
        cart_items, package_drafts, total_price = CartService.get_cart_info(user=request.user)
        serializer = self.get_serializer(cart_items, many=True)
        package_draft_serializer = PackageDraftSerializer(
            package_drafts,
            many=True,
            context=self.get_serializer_context(),
        )

        data = {
            "cart_items": serializer.data,
            "package_drafts": package_draft_serializer.data,
            "total_price": total_price,
        }
        return Response(data)

    def update(self, request, *args, **kwargs):
        """
        장바구니에 담긴 상품의 수량을 변경합니다.
        수량이 0 이하로 들어오면 항목을 삭제합니다.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get("quantity") == 0:
            CartService.update_item(cart_item=instance, data=serializer.validated_data)
            return Response(status=status.HTTP_204_NO_CONTENT)

        updated_instance = serializer.save()
        return Response(self.get_serializer(updated_instance).data)


class PackageDraftViewSet(viewsets.ModelViewSet):
    serializer_class = PackageDraftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartPackageDraftService.get_user_drafts(self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}
