from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models import (
    Brewery,
    Drink,
    Package,
    PackagePolicy,
    Product,
    ProductImage,
)

# ERD 기반 모델 임포트 (products 앱이 수정되었다고 가정)
from apps.users.models import User

from .models import CartItem
from .services import CartPackageDraftService


class CartItemViewSetTest(APITestCase):
    """
    CartItemViewSet에 대한 테스트 클래스.
    Given-When-Then 형식을 주석으로 사용하여 테스트 케이스를 구성합니다.
    """

    @classmethod
    def setUpTestData(cls):
        """
        테스트 전체에서 사용될 공용 데이터를 한 번만 생성합니다.
        """
        # GIVEN: 2명의 사용자
        cls.user = User.objects.create_user(nickname="testuser", email="test@example.com", password="password123")
        cls.other_user = User.objects.create_user(
            nickname="otheruser", email="other@example.com", password="password123"
        )

        # GIVEN: 1개의 양조장
        cls.brewery = Brewery.objects.create(name="테스트 양조장")

        # GIVEN: 1개의 단일 술(Drink) 상품
        cls.drink = Drink.objects.create(
            name="테스트 막걸리",
            brewery=cls.brewery,
            ingredients="쌀, 누룩, 정제수",
            alcohol_type=Drink.AlcoholType.MAKGEOLLI,
            abv=Decimal("6.0"),
            volume_ml=750,
        )

        # GIVEN: 1개의 기획 패키지(Package)
        cls.curated_package = Package.objects.create(name="한잔 추천 세트", type=Package.PackageType.CURATED)
        cls.package_policy = PackagePolicy.objects.create(
            name="2개 구성 정책",
            min_items=2,
            max_items=3,
            allow_duplicate_items=True,
        )

        # GIVEN: 2개의 판매 상품(Product) - 하나는 단일 술, 하나는 패키지
        cls.product_drink = Product.objects.create(
            drink=cls.drink,
            price=10000,
            description="맛있는 테스트 막걸리",
            description_image_url="https://example.com/drink-desc.jpg",
        )
        cls.product_package = Product.objects.create(
            package=cls.curated_package,
            price=25000,
            description="한잔이 추천하는 스페셜 세트",
            description_image_url="https://example.com/package-desc.jpg",
        )

        # GIVEN: 각 상품의 대표 이미지
        ProductImage.objects.create(product=cls.product_drink, image_url="https://example.com/drink.jpg", is_main=True)
        ProductImage.objects.create(
            product=cls.product_package, image_url="https://example.com/package.jpg", is_main=True
        )

    def setUp(self):
        """
        각 테스트 메소드가 실행되기 전에 클라이언트를 인증합니다.
        """
        self.client.force_authenticate(user=self.user)

    def test_add_package_product_to_cart(self):
        """
        [성공] 장바구니에 패키지 상품을 추가하는 경우
        """
        # GIVEN: 장바구니에 추가할 패키지 상품 정보
        url = reverse("cart-item-list")
        data = {
            "product_id": str(self.product_package.id),
            "quantity": 1,
        }

        # WHEN: 장바구니 추가 API를 호출
        response = self.client.post(url, data, format="json")

        # THEN: 새로운 장바구니 항목이 생성되고 201 코드를 반환
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CartItem.objects.filter(user=self.user, product=self.product_package, quantity=1).exists())

    def test_add_inactive_product_to_cart_fails(self):
        """비활성 상품은 장바구니에 담을 수 없다."""
        self.product_package.status = Product.Status.INACTIVE
        self.product_package.save(update_fields=["status", "updated_at"])

        url = reverse("cart-item-list")
        data = {
            "product_id": str(self.product_package.id),
            "quantity": 1,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("비활성", response.data["detail"])

    def test_list_cart_items_and_total_price(self):
        """
        [성공] 장바구니 조회 시 상품 정보와 총액이 올바르게 표시되는 경우
        """
        # GIVEN: 사용자의 장바구니에 2개의 다른 상품이 담겨 있음
        CartItem.objects.create(user=self.user, product=self.product_drink, quantity=3)  # 10000 * 3 = 30000
        CartItem.objects.create(user=self.user, product=self.product_package, quantity=1)  # 25000 * 1 = 25000
        url = reverse("cart-item-list")

        # WHEN: 장바구니 목록 조회 API를 호출
        response = self.client.get(url)

        # THEN: 200 코드와 함께 장바구니 항목 목록 및 총액을 반환
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("cart_items", response.data)
        self.assertIn("package_drafts", response.data)
        self.assertIn("total_price", response.data)
        self.assertEqual(len(response.data["cart_items"]), 2)
        self.assertEqual(response.data["total_price"], 55000)  # 30000 + 25000

    def test_create_package_draft_aggregates_duplicate_products(self):
        """커스텀 패키지는 같은 상품을 중복 row가 아니라 quantity로 합산한다."""
        draft = CartPackageDraftService.create_draft(
            user=self.user,
            policy_id=self.package_policy.id,
            display_name="내가 고른 2병 세트",
            items=[
                {"product_id": str(self.product_drink.id), "quantity": 1},
                {"product_id": str(self.product_drink.id), "quantity": 1},
            ],
        )

        self.assertEqual(draft.items.count(), 1)
        self.assertEqual(draft.items.first().quantity, 2)
        self.assertEqual(draft.final_price, 20000)

    def test_cart_total_includes_package_drafts(self):
        """장바구니 총액은 일반 상품과 커스텀 패키지를 함께 합산한다."""
        CartItem.objects.create(user=self.user, product=self.product_drink, quantity=1)
        CartPackageDraftService.create_draft(
            user=self.user,
            policy_id=self.package_policy.id,
            display_name="내가 고른 세트",
            items=[
                {"product_id": str(self.product_drink.id), "quantity": 1},
                {"product_id": str(self.product_package.id), "quantity": 1},
            ],
        )

        url = reverse("cart-item-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["package_drafts"]), 1)
        self.assertEqual(response.data["total_price"], 45000)

    def test_update_quantity_with_plus_minus_button(self):
        """
        [성공] 장바구니 상품의 수량을 +/- 버튼으로 조작하는 경우
        """
        # GIVEN: 장바구니에 상품이 1개 담겨 있음
        cart_item = CartItem.objects.create(user=self.user, product=self.product_drink, quantity=1)
        url = reverse("cart-item-detail", kwargs={"pk": cart_item.pk})
        data = {"quantity": 5}  # 사용자가 + 버튼을 여러 번 눌러 수량을 5로 변경

        # WHEN: 수량 변경 API(PATCH)를 호출
        response = self.client.patch(url, data, format="json")

        # THEN: 수량이 정상적으로 변경되고 200 코드를 반환
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)
        self.assertEqual(response.data["quantity"], 5)

    def test_remove_item_by_updating_quantity_to_zero(self):
        """
        [성공] 상품 수량을 0으로 업데이트하여 장바구니에서 제거하는 경우
        """
        # GIVEN: 장바구니에 제거할 상품이 존재함
        cart_item = CartItem.objects.create(user=self.user, product=self.product_drink, quantity=3)
        url = reverse("cart-item-detail", kwargs={"pk": cart_item.pk})
        data = {"quantity": 0}  # 사용자가 - 버튼을 눌러 수량을 0으로 변경

        # WHEN: 수량 변경 API(PATCH)를 호출
        response = self.client.patch(url, data, format="json")

        # THEN: 응답은 성공(204 No Content)하며 내용은 비어있고, DB에서 항목은 삭제됨
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(response.data)  # Serializer의 update에서 None을 반환
        self.assertFalse(CartItem.objects.filter(pk=cart_item.pk).exists())

    def test_retrieve_cart_item_success(self):
        """
        [성공] 특정 장바구니 항목을 성공적으로 조회하는 경우
        """
        # GIVEN: 장바구니에 상품이 담겨 있음
        cart_item = CartItem.objects.create(user=self.user, product=self.product_drink, quantity=1)
        url = reverse("cart-item-detail", kwargs={"pk": cart_item.pk})

        # WHEN: 특정 장바구니 항목 조회 API를 호출
        response = self.client.get(url)

        # THEN: 200 코드와 함께 항목 정보를 반환
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], cart_item.pk)
        self.assertEqual(response.data["quantity"], 1)

    def test_retrieve_non_existent_cart_item_fails(self):
        """
        [실패] 존재하지 않는 장바구니 항목을 조회하는 경우
        """
        # GIVEN: 존재하지 않는 장바구니 항목 ID
        non_existent_pk = "99999999-9999-9999-9999-999999999999"  # UUID 형식에 맞게 임의의 값 설정
        url = reverse("cart-item-detail", kwargs={"pk": non_existent_pk})

        # WHEN: 존재하지 않는 장바구니 항목 조회 API를 호출
        response = self.client.get(url)

        # THEN: 404 Not Found 코드를 반환
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_cart_item_success(self):
        """
        [성공] 특정 장바구니 항목을 성공적으로 삭제하는 경우
        """
        # GIVEN: 장바구니에 삭제할 상품이 존재함
        cart_item = CartItem.objects.create(user=self.user, product=self.product_drink, quantity=1)
        url = reverse("cart-item-detail", kwargs={"pk": cart_item.pk})

        # WHEN: 특정 장바구니 항목 삭제 API를 호출
        response = self.client.delete(url)

        # THEN: 204 No Content 코드를 반환하고 DB에서 항목이 삭제됨
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(pk=cart_item.pk).exists())

    def test_delete_non_existent_cart_item_fails(self):
        """
        [실패] 존재하지 않는 장바구니 항목을 삭제하는 경우
        """
        # GIVEN: 존재하지 않는 장바구니 항목 ID
        non_existent_pk = "99999999-9999-9999-9999-999999999999"
        url = reverse("cart-item-detail", kwargs={"pk": non_existent_pk})

        # WHEN: 존재하지 않는 장바구니 항목 삭제 API를 호출
        response = self.client.delete(url)

        # THEN: 404 Not Found 코드를 반환
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_existing_product_to_cart_updates_quantity(self):
        """
        [성공] 장바구니에 이미 있는 상품을 추가할 때 수량이 업데이트되는 경우
        """
        # GIVEN: 장바구니에 이미 상품이 1개 담겨 있음
        CartItem.objects.create(user=self.user, product=self.product_drink, quantity=1)
        url = reverse("cart-item-list")
        data = {
            "product_id": str(self.product_drink.id),
            "quantity": 2,  # 기존 1개에 2개를 더 추가
        }

        # WHEN: 동일 상품을 추가하는 API를 호출
        response = self.client.post(url, data, format="json")

        # THEN: 201 Created 코드를 반환하고 수량이 3으로 업데이트됨
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cart_item = CartItem.objects.get(user=self.user, product=self.product_drink)
        self.assertEqual(cart_item.quantity, 3)  # 1 (기존) + 2 (추가) = 3
        self.assertEqual(response.data["quantity"], 3)

    def test_user_cannot_access_others_cart(self):
        """
        [실패] 다른 사용자의 장바구니에 접근할 수 없는 경우
        """
        # GIVEN: 다른 사용자의 장바구니에 상품이 존재함
        other_cart_item = CartItem.objects.create(user=self.other_user, product=self.product_drink, quantity=1)

        # WHEN: 현재 사용자가 다른 사용자의 아이템을 수정하려고 시도
        detail_url = reverse("cart-item-detail", kwargs={"pk": other_cart_item.pk})
        patch_response = self.client.patch(detail_url, {"quantity": 2})

        # THEN: 다른 사용자의 아이템 접근은 404 에러를 반환
        self.assertEqual(patch_response.status_code, status.HTTP_404_NOT_FOUND)
