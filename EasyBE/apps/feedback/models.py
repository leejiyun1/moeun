from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class FeedbackQuerySet(models.QuerySet):
    """피드백 QuerySet"""

    def high_rated(self):
        """높은 평점 리뷰들 (4점 이상)"""
        return self.filter(rating__gte=4)

    def recent(self, days=7):
        """최근 N일 내 리뷰들"""
        from datetime import timedelta

        from django.utils import timezone

        since = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=since)

    def popular(self):
        """인기 리뷰들 (조회수 기준)"""
        return self.order_by("-view_count", "-created_at")

    def personalized_for_user(self, user):
        """사용자 취향과 비슷한 리뷰들"""
        if hasattr(user, "taste_profile"):
            # TODO: 취향 프로필 기반 필터링 로직
            return self.high_rated().order_by("-created_at")
        return self.high_rated().order_by("-created_at")


class FeedbackManager(models.Manager):
    """피드백 Manager"""

    def get_queryset(self):
        return FeedbackQuerySet(self.model, using=self._db)

    def high_rated(self):
        return self.get_queryset().high_rated()

    def recent(self, days=7):
        return self.get_queryset().recent(days)

    def popular(self):
        return self.get_queryset().popular()

    def personalized_for_user(self, user):
        return self.get_queryset().personalized_for_user(user)


class Feedback(models.Model):
    """상품 피드백/리뷰"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedbacks")
    order_item = models.OneToOneField(
        "orders.OrderItem", on_delete=models.CASCADE, related_name="feedback", help_text="피드백을 작성한 주문 아이템"
    )

    # 종합 평점 (별점 1-5)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="종합 평점 (1-5점)"
    )

    # 텍스트 피드백
    comment = models.TextField(null=True, blank=True, help_text="상세 피드백 내용")

    # 이미지 필드 (S3/NCP URL 저장)
    image_url = models.URLField(null=True, blank=True, max_length=500, help_text="피드백 이미지 URL (S3/NCP 저장소)")

    # 조회 관련
    view_count = models.PositiveIntegerField(default=0, help_text="피드백 조회수")
    last_viewed_at = models.DateTimeField(null=True, blank=True, help_text="마지막 조회 일시")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager 설정
    objects = FeedbackManager()

    class Meta:
        db_table = "feedbacks"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["order_item"]),
            models.Index(fields=["rating", "created_at"]),
            models.Index(fields=["view_count"]),
        ]

    def __str__(self):
        return f"{self.user.nickname} - {self.order_item.product.name} ({self.rating}점)"

    @property
    def product(self):
        """피드백 대상 상품"""
        return self.order_item.product

    @property
    def masked_username(self):
        """사용자명 마스킹 처리 (abc**** 형태)"""
        username = self.user.nickname or self.user.username
        if len(username) <= 3:
            return username[0] + "*" * (len(username) - 1)
        return username[:3] + "*" * (len(username) - 3)

    @property
    def has_image(self):
        """이미지가 있는지 확인"""
        return bool(self.image_url)

    def increment_view_count(self):
        """조회수 증가"""
        from django.utils import timezone

        self.view_count += 1
        self.last_viewed_at = timezone.now()
        self.save(update_fields=["view_count", "last_viewed_at"])

    def delete_image(self):
        """이미지 삭제 (S3/NCP에서)"""
        if self.image_url:
            from core.utils.ncloud_manager import S3Uploader

            uploader = S3Uploader()
            success = uploader.delete_file(self.image_url)
            if success:
                self.image_url = None
                self.save(update_fields=["image_url"])
            return success
        return True

    def save(self, *args, **kwargs):
        """피드백 저장 시 상품 리뷰 수를 갱신한다."""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # 상품의 review_count 증가
            product = self.order_item.product
            product.review_count += 1
            product.save(update_fields=["review_count"])

    def delete(self, *args, **kwargs):
        """피드백 삭제 시 상품의 리뷰 수 감소 및 이미지 삭제"""
        # 이미지 삭제
        self.delete_image()

        # 상품 리뷰 수 감소
        product = self.order_item.product
        product.review_count -= 1
        product.save(update_fields=["review_count"])

        super().delete(*args, **kwargs)
