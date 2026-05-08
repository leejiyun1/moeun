from django.contrib import admin

from apps.orders.models import (
    Order,
    OrderCustomPackage,
    OrderCustomPackageItem,
    OrderItem,
    Payment,
)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "user",
        "total_price",
        "status",
        "payment_status",
        "fulfillment_method",
        "is_test_order",
        "created_at",
    ]
    list_filter = ["status", "payment_status", "fulfillment_method", "is_test_order"]
    search_fields = ["order_number", "user__email", "user__nickname"]
    readonly_fields = ["order_number", "created_at", "updated_at"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["merchant_uid", "order", "provider", "amount", "status", "is_test_payment", "approved_at"]
    list_filter = ["provider", "status", "is_test_payment"]
    search_fields = ["merchant_uid", "payment_key", "order__order_number"]
    readonly_fields = ["created_at", "updated_at", "approved_at"]


admin.site.register(OrderItem)
admin.site.register(OrderCustomPackage)
admin.site.register(OrderCustomPackageItem)
