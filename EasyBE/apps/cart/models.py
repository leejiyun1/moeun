from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.products.models import PackagePolicy, Product
from apps.stores.models import Store


class CartItem(models.Model):
    """장바구니 아이템"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1, help_text="수량")
    pickup_store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart_items_for_pickup",
        help_text="픽업 매장",
    )
    pickup_date = models.DateField(null=True, blank=True, help_text="픽업 날짜")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "장바구니 항목"
        verbose_name_plural = "장바구니 항목 목록"
        db_table = "cart_items"
        unique_together = ("user", "product", "pickup_store", "pickup_date")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.nickname} - {self.product.name} x{self.quantity}"

    @property
    def total_price(self):
        """해당 아이템의 총 가격"""
        return self.product.price * self.quantity


class PackageDraft(models.Model):
    """사용자가 장바구니에서 구성 중인 커스텀 패키지."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "작성 중"
        READY = "READY", "주문 가능"
        ORDERED = "ORDERED", "주문 완료"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="package_drafts")
    policy = models.ForeignKey(PackagePolicy, on_delete=models.PROTECT, related_name="package_drafts")
    display_name = models.CharField(max_length=80, help_text="사용자에게 표시할 패키지명")
    base_price = models.PositiveIntegerField(default=0, help_text="구성품 합산가")
    discount_amount = models.PositiveIntegerField(default=0, help_text="정책 할인 금액")
    final_price = models.PositiveIntegerField(default=0, help_text="최종 패키지 가격")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    pickup_store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="package_drafts_for_pickup",
        help_text="픽업 매장",
    )
    pickup_date = models.DateField(null=True, blank=True, help_text="픽업 날짜")
    is_tasting_selected = models.BooleanField(default=False, help_text="시음 선택 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "package_drafts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["policy"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.nickname} - {self.display_name}"


class PackageDraftItem(models.Model):
    """커스텀 패키지 draft 구성품."""

    draft = models.ForeignKey(PackageDraft, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="package_draft_items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], help_text="구성 수량")
    sort_order = models.PositiveIntegerField(default=0, help_text="노출 순서")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "package_draft_items"
        unique_together = ("draft", "product")
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["draft", "sort_order"]),
            models.Index(fields=["product"]),
        ]

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.draft.display_name} - {self.product.name} x{self.quantity}"
