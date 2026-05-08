from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.orders.views import AdminOrderListView, OrderItemListViewSet, OrderViewSet

app_name = "orders"

router = DefaultRouter()
router.register(r"order-items", OrderItemListViewSet, basename="order-item")

urlpatterns = [
    path("", include(router.urls)),
    # OrderViewSet의 URL들을 수동으로 등록
    path("manage/", AdminOrderListView.as_view(), name="orders-manage-list"),
    path("create_from_cart/", OrderViewSet.as_view({"post": "create_from_cart"}), name="order-create-from-cart"),
    path(
        "<int:pk>/test-payment/confirm/",
        OrderViewSet.as_view({"post": "confirm_test_payment"}),
        name="order-test-payment-confirm",
    ),
    path(
        "toss-payment/confirm/",
        OrderViewSet.as_view({"post": "confirm_toss_payment"}),
        name="order-toss-payment-confirm",
    ),
    path("", OrderViewSet.as_view({"get": "list"}), name="order-list"),
    path("<int:pk>/", OrderViewSet.as_view({"get": "retrieve"}), name="order-detail"),
]
