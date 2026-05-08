from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Order(models.Model):
    """주문"""

    class Status(models.TextChoices):
        PENDING_PAYMENT = "PENDING_PAYMENT", "결제 대기"
        PENDING = "PENDING", "주문 완료"
        CONFIRMED = "CONFIRMED", "주문 확인"
        READY = "READY", "픽업 준비 완료"
        COMPLETED = "COMPLETED", "픽업 완료"
        CANCELLED = "CANCELLED", "주문 취소"

    class PaymentStatus(models.TextChoices):
        READY = "READY", "결제 대기"
        PAID = "PAID", "결제 완료"
        FAILED = "FAILED", "결제 실패"
        CANCELLED = "CANCELLED", "결제 취소"
        REFUNDED = "REFUNDED", "환불 완료"

    class FulfillmentMethod(models.TextChoices):
        PICKUP = "PICKUP", "매장 수령"
        DELIVERY = "DELIVERY", "배송"
        UNDECIDED = "UNDECIDED", "미정"

    id = models.BigAutoField(primary_key=True)
    order_number = models.CharField(max_length=20, unique=True, help_text="사용자에게 보여줄 주문 번호")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    # 주문 금액
    total_price = models.PositiveIntegerField(help_text="총 주문 금액")

    # 주문/결제/수령 상태
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.READY)
    fulfillment_method = models.CharField(
        max_length=20,
        choices=FulfillmentMethod.choices,
        default=FulfillmentMethod.PICKUP,
    )
    is_test_order = models.BooleanField(default=True, help_text="테스트 결제 주문 여부")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["order_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["fulfillment_method"]),
            models.Index(fields=["is_test_order"]),
            models.Index(fields=["-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """주문 번호 생성 (예: ORD20250107001)"""
        today = timezone.now().strftime("%Y%m%d")

        # 오늘 생성된 주문 수 + 1
        today_orders_count = Order.objects.filter(created_at__date=timezone.now().date()).count()

        sequence = str(today_orders_count + 1).zfill(3)
        return f"ORD{today}{sequence}"

    def __str__(self):
        return f"주문 {self.order_number} - {self.user.nickname}"

    def can_cancel(self):
        """취소 가능한지 확인"""
        return self.status in [self.Status.PENDING_PAYMENT, self.Status.PENDING, self.Status.CONFIRMED]

    def cancel(self):
        """주문 취소"""
        if self.can_cancel():
            self.status = self.Status.CANCELLED
            self.save(update_fields=["status", "updated_at"])

            return True
        return False

    def mark_ready(self):
        """픽업 준비 완료"""
        if self.status == self.Status.CONFIRMED:
            self.status = self.Status.READY
            self.save(update_fields=["status", "updated_at"])

    def complete(self):
        """주문 완료 (픽업 완료)"""
        if self.status == self.Status.READY:
            self.status = self.Status.COMPLETED
            self.save(update_fields=["status", "updated_at"])

    def mark_paid(self):
        """결제 완료 처리"""
        self.payment_status = self.PaymentStatus.PAID
        self.status = self.Status.CONFIRMED
        self.save(update_fields=["payment_status", "status", "updated_at"])


class Payment(models.Model):
    """주문 결제 내역."""

    class Provider(models.TextChoices):
        TEST = "TEST", "테스트 결제"
        TOSS_TEST = "TOSS_TEST", "토스페이먼츠 테스트 결제"

    class Status(models.TextChoices):
        READY = "READY", "결제 대기"
        PAID = "PAID", "결제 완료"
        FAILED = "FAILED", "결제 실패"
        CANCELLED = "CANCELLED", "결제 취소"
        REFUNDED = "REFUNDED", "환불 완료"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.TEST)
    payment_key = models.CharField(max_length=120, blank=True, help_text="PG 결제 식별자")
    merchant_uid = models.CharField(max_length=80, unique=True, help_text="내부 결제 주문번호")
    amount = models.PositiveIntegerField(help_text="결제 금액")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.READY)
    is_test_payment = models.BooleanField(default=True, help_text="테스트 결제 여부")
    approved_at = models.DateTimeField(null=True, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["merchant_uid"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_test_payment"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.order.order_number} - {self.provider} {self.status}"

    def mark_paid(self, payment_key: str, raw_response: dict | None = None):
        self.payment_key = payment_key
        self.status = self.Status.PAID
        self.approved_at = timezone.now()
        self.raw_response = raw_response or {}
        self.save(update_fields=["payment_key", "status", "approved_at", "raw_response", "updated_at"])

    def mark_failed(self, raw_response: dict | None = None):
        self.status = self.Status.FAILED
        self.raw_response = raw_response or {}
        self.save(update_fields=["status", "raw_response", "updated_at"])


class OrderItem(models.Model):
    """주문 아이템"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="order_items")

    # 주문 당시의 가격 (가격 변동에 영향 받지 않도록)
    price = models.PositiveIntegerField(help_text="주문 당시 상품 단가")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="주문 수량")

    # 픽업 정보
    pickup_store = models.ForeignKey(
        "stores.Store", on_delete=models.CASCADE, related_name="order_items", help_text="픽업 매장"
    )
    pickup_day = models.DateField(help_text="픽업 예정 날짜")
    pickup_status = models.BooleanField(default=False, help_text="픽업 완료 여부")

    # 선물 관련

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_items"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
            models.Index(fields=["pickup_store"]),
            models.Index(fields=["pickup_day"]),
            models.Index(fields=["pickup_status"]),
        ]

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name} x{self.quantity}"

    @property
    def total_price(self):
        """해당 아이템의 총 가격"""
        return self.price * self.quantity

    def mark_picked_up(self):
        """픽업 완료 처리"""
        self.pickup_status = True
        self.save(update_fields=["pickup_status"])

        # 모든 아이템이 픽업 완료되면 주문 완료
        if not self.order.items.filter(pickup_status=False).exists():
            self.order.complete()

    def can_pickup(self):
        """픽업 가능한지 확인"""
        return self.order.status in [Order.Status.CONFIRMED, Order.Status.READY] and not self.pickup_status


class OrderCustomPackage(models.Model):
    """주문 시점에 고정된 커스텀 패키지 snapshot."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="custom_packages")
    source_draft = models.ForeignKey(
        "cart.PackageDraft",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_snapshots",
    )
    display_name = models.CharField(max_length=80)
    package_policy_name = models.CharField(max_length=50)
    base_price = models.PositiveIntegerField(help_text="구성품 합산가")
    discount_amount = models.PositiveIntegerField(default=0, help_text="정책 할인 금액")
    final_price = models.PositiveIntegerField(help_text="최종 패키지 가격")
    pickup_store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="order_custom_packages")
    pickup_day = models.DateField(help_text="픽업 예정 날짜")
    pickup_status = models.BooleanField(default=False, help_text="픽업 완료 여부")
    is_tasting_selected = models.BooleanField(default=False, help_text="시음 선택 여부")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_custom_packages"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["pickup_store"]),
            models.Index(fields=["pickup_day"]),
            models.Index(fields=["pickup_status"]),
        ]

    def __str__(self):
        return f"{self.order.order_number} - {self.display_name}"

    def mark_picked_up(self):
        self.pickup_status = True
        self.save(update_fields=["pickup_status"])


class OrderCustomPackageItem(models.Model):
    """주문 커스텀 패키지 구성품 snapshot."""

    custom_package = models.ForeignKey(OrderCustomPackage, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="order_custom_package_items")
    product_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField(help_text="주문 당시 상품 단가")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_custom_package_items"
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["custom_package", "sort_order"]),
            models.Index(fields=["product"]),
        ]

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.custom_package.display_name} - {self.product_name} x{self.quantity}"
