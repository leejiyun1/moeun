# apps/products/services/product_service.py

from django.db.models import F

from apps.products.models import Product
from apps.products.selectors import ProductSelector


class ProductService:
    """상품 관련 비즈니스 로직"""

    @staticmethod
    def get_product_detail(product_id: str) -> Product:
        """
        상품 상세 조회 (조회수 증가 포함)

        Args:
            product_id: 상품 ID

        Returns:
            Product: 조회수가 증가된 상품 객체

        Raises:
            Http404: 상품이 존재하지 않거나 비활성 상태일 때
        """
        ProductSelector.get_active_product_or_404(product_id)

        # 조회수 증가
        ProductService.increment_view_count(product_id)

        # 업데이트된 상품 객체 반환
        return ProductSelector.get_active_product_or_404(product_id)

    @staticmethod
    def increment_view_count(product_id: str) -> None:
        """
        상품 조회수 증가

        Args:
            product_id: 상품 ID
        """
        Product.objects.filter(pk=product_id).update(view_count=F("view_count") + 1)

    @staticmethod
    def get_product_for_management(product_id: str) -> Product:
        """
        관리자용 상품 조회 (모든 상태 포함)

        Args:
            product_id: 상품 ID

        Returns:
            Product: 상품 객체
        """
        return ProductSelector.get_management_product_or_404(product_id)
