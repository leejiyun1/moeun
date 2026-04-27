# apps/products/models.py

import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Brewery(models.Model):
    """양조장 정보"""

    name = models.CharField(max_length=100, help_text="양조장명")
    region = models.CharField(max_length=30, null=True, blank=True, help_text="지역")
    address = models.TextField(null=True, blank=True, help_text="주소")
    phone = models.CharField(max_length=20, null=True, blank=True, help_text="연락처")
    description = models.TextField(null=True, blank=True, help_text="양조장 설명")
    image_url = models.URLField(max_length=255, null=True, blank=True, help_text="양조장 이미지 URL")
    is_active = models.BooleanField(default=True, help_text="활성 상태")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "breweries"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["region"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class Drink(models.Model):
    """개별 술 정보"""

    class AlcoholType(models.TextChoices):
        MAKGEOLLI = "MAKGEOLLI", "막걸리"
        YAKJU = "YAKJU", "약주"
        CHEONGJU = "CHEONGJU", "청주"
        SOJU = "SOJU", "소주"
        FRUIT_WINE = "FRUIT_WINE", "과실주"

    # 공통 validators
    TASTE_LEVEL_VALIDATORS = [MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("5.0"))]
    ABV_VALIDATORS = [MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))]

    name = models.CharField(max_length=100, help_text="술 이름")
    brewery = models.ForeignKey(Brewery, on_delete=models.CASCADE, related_name="drinks")
    ingredients = models.TextField(help_text="원재료")
    alcohol_type = models.CharField(max_length=20, choices=AlcoholType.choices, help_text="주종")
    abv = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=ABV_VALIDATORS,
        help_text="알코올 도수(%)",
    )
    volume_ml = models.PositiveIntegerField(help_text="용량(ml)")

    # 맛 프로필 (0.0 ~ 5.0)
    sweetness_level = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=TASTE_LEVEL_VALIDATORS,
        help_text="단맛 (0.0~5.0)",
    )
    acidity_level = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=TASTE_LEVEL_VALIDATORS,
        help_text="산미 (0.0~5.0)",
    )
    body_level = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=TASTE_LEVEL_VALIDATORS,
        help_text="바디감 (0.0~5.0)",
    )
    carbonation_level = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=TASTE_LEVEL_VALIDATORS,
        help_text="탄산감 (0.0~5.0)",
    )
    bitterness_level = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=TASTE_LEVEL_VALIDATORS,
        help_text="쓴맛 (0.0~5.0)",
    )
    aroma_level = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=TASTE_LEVEL_VALIDATORS,
        help_text="풍미 (0.0~5.0)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "drinks"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["alcohol_type"]),
            models.Index(fields=["abv"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.abv}%)"


class Package(models.Model):
    """패키지 (세트 상품)"""

    class PackageType(models.TextChoices):
        CURATED = "CURATED", "큐레이티드"

    name = models.CharField(max_length=30, help_text="패키지명")
    type = models.CharField(
        max_length=10, choices=PackageType.choices, default=PackageType.CURATED, help_text="패키지 타입"
    )
    policy = models.ForeignKey(
        "PackagePolicy",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="packages",
        help_text="패키지 적용 정책",
    )
    drinks = models.ManyToManyField(Drink, through="PackageItem", related_name="packages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "packages"
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class PackagePolicy(models.Model):
    """패키지 구성/할인 정책."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "활성"
        INACTIVE = "INACTIVE", "비활성"

    class AllowedItemScope(models.TextChoices):
        ALL_PRODUCTS = "ALL_PRODUCTS", "모든 상품"
        SINGLE_PRODUCTS = "SINGLE_PRODUCTS", "단일 상품만"
        PACKAGE_PRODUCTS = "PACKAGE_PRODUCTS", "패키지 상품만"
        ALLOWED_SET = "ALLOWED_SET", "허용 상품만"

    class DiscountType(models.TextChoices):
        NONE = "NONE", "없음"
        FIXED_AMOUNT = "FIXED_AMOUNT", "정액 할인"

    name = models.CharField(max_length=50, help_text="정책명")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    min_items = models.PositiveIntegerField(default=2, validators=[MinValueValidator(1)], help_text="최소 구성 수량")
    max_items = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1)], help_text="최대 구성 수량")
    allow_duplicate_items = models.BooleanField(default=False, help_text="같은 상품 중복 허용 여부")
    allowed_item_scope = models.CharField(
        max_length=30,
        choices=AllowedItemScope.choices,
        default=AllowedItemScope.SINGLE_PRODUCTS,
        help_text="허용 상품 범위",
    )
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.NONE)
    discount_value = models.PositiveIntegerField(default=0, help_text="할인 금액")
    allowed_products = models.ManyToManyField(
        "Product",
        through="PackagePolicyAllowedProduct",
        blank=True,
        related_name="package_policies",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "package_policies"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["allowed_item_scope"]),
        ]

    def clean(self):
        if self.min_items > self.max_items:
            raise ValidationError("최소 구성 수량은 최대 구성 수량보다 클 수 없습니다.")
        if self.discount_type == self.DiscountType.NONE and self.discount_value:
            raise ValidationError("할인 없음 정책에서는 할인 금액을 설정할 수 없습니다.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PackageItem(models.Model):
    """패키지에 포함된 술들"""

    drink = models.ForeignKey(Drink, on_delete=models.CASCADE, related_name="package_items")
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], help_text="구성 수량")
    sort_order = models.PositiveIntegerField(default=0, help_text="노출 순서")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "package_items"
        unique_together = ("drink", "package")
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["package", "sort_order"]),
            models.Index(fields=["drink"]),
        ]

    def __str__(self):
        return f"{self.package.name} - {self.drink.name} x{self.quantity}"


class Product(models.Model):
    """상품 (개별 술 또는 패키지)"""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "활성"
        INACTIVE = "INACTIVE", "비활성"
        OUT_OF_STOCK = "OUT_OF_STOCK", "품절"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 상품은 개별 술이거나 패키지 중 하나
    drink = models.OneToOneField(
        Drink, on_delete=models.CASCADE, null=True, blank=True, related_name="product", help_text="개별 술"
    )
    package = models.OneToOneField(
        Package, on_delete=models.CASCADE, null=True, blank=True, related_name="product", help_text="패키지"
    )

    # 가격 정보
    price = models.PositiveIntegerField(help_text="판매가격")
    original_price = models.PositiveIntegerField(null=True, blank=True, help_text="정가")
    discount = models.PositiveIntegerField(null=True, blank=True, help_text="할인금액")

    # 상품 설명
    description = models.TextField(help_text="상품 설명")
    description_image_url = models.URLField(max_length=255, help_text="상품 설명 이미지 URL")

    # 상품 특성
    is_gift_suitable = models.BooleanField(default=False, help_text="선물 적합")
    is_award_winning = models.BooleanField(default=False, help_text="수상작")
    is_regional_specialty = models.BooleanField(default=False, help_text="지역 특산주")
    is_limited_edition = models.BooleanField(default=False, help_text="리미티드 에디션")
    is_premium = models.BooleanField(default=False, help_text="프리미엄")
    is_organic = models.BooleanField(default=False, help_text="유기농")

    # 통계
    view_count = models.PositiveIntegerField(default=0, help_text="조회수")
    order_count = models.PositiveIntegerField(default=0, help_text="주문수")
    like_count = models.PositiveIntegerField(default=0, help_text="좋아요 수")
    review_count = models.PositiveIntegerField(default=0, help_text="리뷰 수")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, help_text="상태")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["status"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["-view_count"]),
            models.Index(fields=["-order_count"]),
        ]

    def clean(self):
        """drink와 package 중 하나는 반드시 있어야 함"""
        if not self.drink and not self.package:
            raise ValidationError("상품은 개별 술이거나 패키지 중 하나여야 합니다.")
        if self.drink and self.package:
            raise ValidationError("상품은 개별 술과 패키지를 동시에 가질 수 없습니다.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.drink:
            return f"상품: {self.drink.name}"
        elif self.package:
            return f"상품: {self.package.name}"
        return f"상품 ID: {self.id}"

    @property
    def name(self):
        """상품명 반환"""
        if self.drink:
            return self.drink.name
        elif self.package:
            return self.package.name
        return "Unknown Product"

    @property
    def product_type(self):
        """상품 타입 반환"""
        if self.drink:
            return "individual"
        elif self.package:
            return "package"
        return "unknown"

    def get_discount_rate(self):
        """할인율 계산 (퍼센트)"""
        if self.original_price and self.discount:
            return round((self.discount / self.original_price) * 100, 1)
        return 0

    def get_final_price(self):
        """최종 판매가 계산"""
        return self.price

    def is_on_sale(self):
        """할인 중인지 확인"""
        return bool(self.discount and self.discount > 0)

    @property
    def savings_amount(self):
        """절약 금액"""
        return self.discount if self.discount else 0


class ProductImage(models.Model):
    """상품 이미지"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(max_length=255, help_text="이미지 URL")
    is_main = models.BooleanField(default=False, help_text="메인 이미지 여부")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_images"
        indexes = [
            models.Index(fields=["product", "is_main"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["product"], condition=models.Q(is_main=True), name="unique_main_image_per_product"
            )
        ]

    def clean(self):
        """메인 이미지는 상품당 하나만 허용"""
        if self.is_main:
            existing_main = ProductImage.objects.filter(product=self.product, is_main=True).exclude(pk=self.pk)
            if existing_main.exists():
                raise ValidationError("상품당 메인 이미지는 하나만 설정할 수 있습니다.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {'메인' if self.is_main else '서브'} 이미지"


class ProductLike(models.Model):
    """상품 좋아요"""

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="liked_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_likes"
        unique_together = ("user", "product")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.user.nickname} - {self.product.name}"


class PackagePolicyAllowedProduct(models.Model):
    """패키지 정책에서 명시적으로 허용한 상품."""

    policy = models.ForeignKey(PackagePolicy, on_delete=models.CASCADE, related_name="allowed_product_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="allowed_package_policy_items")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "package_policy_allowed_products"
        unique_together = ("policy", "product")
        indexes = [
            models.Index(fields=["policy"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.policy.name} - {self.product.name}"
