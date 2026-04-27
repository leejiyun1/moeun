# apps/products/views/product/admin.py

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.products.selectors import PackagePolicySelector, ProductSelector
from apps.products.serializers.drink import DrinkForPackageSerializer
from apps.products.serializers.package_policy import PackagePolicySerializer
from apps.products.serializers.product.create import (
    IndividualProductCreateSerializer,
    PackageProductCreateSerializer,
)
from apps.products.serializers.product.detail import ProductDetailSerializer
from apps.products.serializers.product.list import ProductListSerializer
from apps.products.serializers.product.update import ProductUpdateSerializer
from apps.products.services import PackagePolicyCommandService, ProductCommandService

from ..pagination import SearchPagination

# ============================================================================
# 관리자용 제품 관리 API
# ============================================================================


class IndividualProductCreateView(CreateAPIView):
    """개별 상품 생성 (관리자용)"""

    serializer_class = IndividualProductCreateSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="개별 상품 생성",
        description="""
        새로운 술과 개별 상품을 동시에 생성합니다. (관리자용)
        """,
        tags=["관리자 - 제품 관리"],
    )
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class PackageProductCreateView(CreateAPIView):
    """패키지 상품 생성 (관리자용)"""

    serializer_class = PackageProductCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="패키지 상품 생성",
        description="""
        기존 술들을 선택해서 패키지와 상품을 생성합니다. (관리자용)
        """,
        tags=["관리자 - 제품 관리"],
    )
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class DrinksForPackageView(ListAPIView):
    """패키지 생성용 술 목록 조회 (관리자용)"""

    serializer_class = DrinkForPackageSerializer
    pagination_class = SearchPagination
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="패키지 생성용 술 목록",
        description="""
        패키지에 포함할 수 있는 술들의 목록을 조회합니다. (관리자용)
        """,
        tags=["관리자 - 제품 관리"],
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """상품이 있는 술들만 반환"""
        return ProductSelector.get_drinks_for_package_queryset()


class PackagePolicyManageListView(ListCreateAPIView):
    """패키지 정책 목록/생성 (관리자용)"""

    serializer_class = PackagePolicySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SearchPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "updated_at", "status", "min_items", "max_items"]
    ordering = ["-created_at"]

    @extend_schema(
        summary="패키지 정책 목록",
        description="패키지 구성/할인 정책 목록을 조회합니다.",
        tags=["관리자 - 패키지 정책"],
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="패키지 정책 생성", description="패키지 구성/할인 정책을 생성합니다.", tags=["관리자 - 패키지 정책"]
    )
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        return PackagePolicySelector.management_queryset()


class PackagePolicyManageView(RetrieveUpdateDestroyAPIView):
    """패키지 정책 조회/수정/비활성화 (관리자용)"""

    serializer_class = PackagePolicySerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="패키지 정책 조회", description="패키지 구성/할인 정책을 조회합니다.", tags=["관리자 - 패키지 정책"]
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)

    @extend_schema(
        summary="패키지 정책 수정",
        description="패키지 구성/할인 정책을 부분 수정합니다.",
        tags=["관리자 - 패키지 정책"],
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="패키지 정책 비활성화",
        description="패키지 정책을 삭제하지 않고 비활성화합니다.",
        tags=["관리자 - 패키지 정책"],
    )
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return PackagePolicySelector.management_queryset()

    def perform_destroy(self, instance):
        PackagePolicyCommandService.deactivate_policy(instance)


class ProductManageView(RetrieveUpdateDestroyAPIView):
    """제품 관리 (관리자용)"""

    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    @extend_schema(
        summary="제품 관리 - 조회",
        description="""
        제품의 상세 정보를 조회합니다. (관리자용)
        모든 상태의 제품을 조회할 수 있습니다.
        """,
        tags=["관리자 - 제품 관리"],
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def put(self, request, *args, **kwargs):
        return self._update_product(request)

    @extend_schema(summary="제품 정보 수정", description="제품 정보를 부분 수정합니다.", tags=["관리자 - 제품 관리"])
    def patch(self, request, *args, **kwargs):
        return self._update_product(request)

    @extend_schema(
        summary="제품 삭제",
        description="""
        제품을 삭제합니다.
        """,
        tags=["관리자 - 제품 관리"],
    )
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """관리자는 모든 상태의 제품 조회 가능"""
        return ProductSelector.management_queryset()

    def perform_destroy(self, instance):
        """관리자 삭제는 참조 보존을 위해 비활성화로 처리한다."""
        ProductCommandService.deactivate_product(instance)

    def _update_product(self, request):
        product = self.get_object()
        serializer = ProductUpdateSerializer(instance=product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        product = ProductCommandService.update_product(product, serializer.validated_data)
        product = ProductSelector.get_management_product_or_404(product.pk)
        return Response(ProductDetailSerializer(product).data)


class ProductManageListView(ListAPIView):
    """제품 목록 관리 (관리자용)"""

    serializer_class = ProductListSerializer
    pagination_class = SearchPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["drink__name", "package__name", "description"]
    ordering_fields = ["price", "created_at", "view_count", "status"]
    ordering = ["-created_at"]

    @extend_schema(
        summary="제품 목록 관리",
        description="""
        모든 제품의 목록을 조회합니다. (관리자용)
        """,
        tags=["관리자 - 제품 관리"],
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """관리자는 모든 상태의 제품 조회 가능"""
        return ProductSelector.get_management_list_queryset(self.request.query_params.get("status"))
