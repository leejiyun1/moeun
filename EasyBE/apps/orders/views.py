from datetime import date

from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.orders.models import Order, OrderItem
from apps.orders.serializers import (
    FlatOrderItemSerializer,
    OrderSerializer,
    TestPaymentConfirmSerializer,
)
from apps.orders.services import (
    AdultVerificationRequiredError,
    CartIsEmptyError,
    InvalidCartSelectionError,
    MissingPickupInfoError,
    OrderCreationError,
    OrderService,
    PaymentError,
)
from apps.users.permissions import IsAdminRole


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("payment")
            .prefetch_related(
                "items__product",
                "items__pickup_store",
                "custom_packages__pickup_store",
                "custom_packages__items__product__images",
            )
            .order_by("-created_at")
        )

    @action(detail=False, methods=["post"])
    def create_from_cart(self, request, *args, **kwargs):
        """
        장바구니의 모든 상품으로 주문을 생성
        """
        try:
            has_selection = "item_ids" in request.data or "package_draft_ids" in request.data
            order = OrderService.create_order_from_cart(
                user=request.user,
                cart_item_ids=request.data.get("item_ids", []) if has_selection else None,
                package_draft_ids=request.data.get("package_draft_ids", []) if has_selection else None,
                fulfillment_method=request.data.get("fulfillment_method", Order.FulfillmentMethod.PICKUP),
                is_test_order=True,
            )
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except AdultVerificationRequiredError as e:
            return Response({"code": "ADULT_VERIFICATION_REQUIRED", "detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except (CartIsEmptyError, MissingPickupInfoError, InvalidCartSelectionError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except OrderCreationError as e:
            # 기타 주문 생성 관련 예외 처리
            return Response(
                {"detail": f"주문 생성 중 오류가 발생했습니다: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"], url_path="test-payment/confirm")
    def confirm_test_payment(self, request, pk=None):
        serializer = TestPaymentConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = OrderService.confirm_test_payment(
                user=request.user,
                order_id=pk,
                payment_key=serializer.validated_data["payment_key"],
            )
        except PaymentError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(order).data, status=status.HTTP_200_OK)


class OrderItemListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FlatOrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            OrderItem.objects.filter(order__user=self.request.user)
            .select_related("order", "product", "pickup_store")
            .order_by("-order__created_at", "-id")
        )


class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        queryset = (
            Order.objects.select_related("user", "payment")
            .prefetch_related(
                "items__product__images",
                "items__pickup_store",
                "custom_packages__pickup_store",
                "custom_packages__items__product__images",
            )
            .order_by("-created_at")
        )

        status_filter = self.request.query_params.get("status")
        payment_status = self.request.query_params.get("payment_status")
        is_test_order = self.request.query_params.get("is_test_order")

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        if is_test_order in {"true", "false"}:
            queryset = queryset.filter(is_test_order=is_test_order == "true")

        return queryset
