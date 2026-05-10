from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.cart.models import CartItem
from apps.cart.services import CartPackageDraftService
from apps.orders.models import Order, OrderCustomPackage, Payment
from apps.products.models import Brewery, Drink, PackagePolicy, Product
from apps.stores.models import Store

User = get_user_model()


class OrderFromCartAPITest(APITestCase):
    def setUp(self):
        # Given: 기본 데이터 설정
        self.user = User.objects.create_user(nickname="testuser")
        self.user.verify_adult()
        self.client.force_authenticate(user=self.user)

        self.brewery = Brewery.objects.create(name="Test Brewery")

        # Drink 객체 생성
        self.drink1 = Drink.objects.create(
            name="Test Drink 1",
            brewery=self.brewery,
            ingredients="Ingredients 1",
            alcohol_type=Drink.AlcoholType.MAKGEOLLI,
            abv=Decimal("6.0"),
            volume_ml=750,
        )
        self.drink2 = Drink.objects.create(
            name="Test Drink 2",
            brewery=self.brewery,
            ingredients="Ingredients 2",
            alcohol_type=Drink.AlcoholType.SOJU,
            abv=Decimal("19.0"),
            volume_ml=360,
        )

        # Product 객체 생성 (Drink와 연결)
        self.product1 = Product.objects.create(
            drink=self.drink1, price=10000, description="Desc 1", description_image_url="http://example.com/desc1.jpg"
        )
        self.product2 = Product.objects.create(
            drink=self.drink2, price=20000, description="Desc 2", description_image_url="http://example.com/desc2.jpg"
        )

        # 매장 설정
        self.store1 = Store.objects.create(name="Store 1", address="Address 1")
        self.store2 = Store.objects.create(name="Store 2", address="Address 2")
        self.package_policy = PackagePolicy.objects.create(
            name="커스텀 2병 정책",
            min_items=2,
            max_items=3,
            allow_duplicate_items=True,
        )

        # URL
        self.create_order_url = "/api/v1/orders/create_from_cart/"

    def pickup_payload(self, **extra):
        payload = {
            "fulfillment_method": Order.FulfillmentMethod.PICKUP,
            "pickup_store_id": self.store1.id,
            "pickup_date": str(date.today()),
        }
        payload.update(extra)
        return payload

    def test_create_order_from_cart_success(self):
        """장바구니에서 주문 생성 성공 테스트"""
        # Given: 장바구니에 상품 추가
        CartItem.objects.create(
            user=self.user, product=self.product1, quantity=2, pickup_store=self.store1, pickup_date=date.today()
        )
        CartItem.objects.create(
            user=self.user, product=self.product2, quantity=1, pickup_store=self.store1, pickup_date=date.today()
        )

        # When: 주문 생성 API 호출
        response = self.client.post(self.create_order_url, self.pickup_payload(), format="json")

        # Then: 주문이 성공적으로 생성되고, 장바구니가 비워짐
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.total_price, 40000)  # (10000 * 2) + (20000 * 1)
        self.assertEqual(order.items.count(), 2)
        self.assertTrue(order.is_test_order)
        self.assertEqual(order.status, Order.Status.PENDING_PAYMENT)
        self.assertEqual(order.payment_status, Order.PaymentStatus.READY)
        self.assertEqual(order.fulfillment_method, Order.FulfillmentMethod.PICKUP)
        self.assertEqual(order.pickup_store, self.store1)
        self.assertEqual(order.pickup_day, date.today())
        self.assertEqual(order.payment.amount, 40000)
        self.assertEqual(order.payment.status, Payment.Status.READY)

        # 장바구니 비워졌는지 확인
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)

    def test_confirm_test_payment_success(self):
        """테스트 결제 승인 시 주문과 결제 상태가 완료로 변경된다."""
        CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=1,
            pickup_store=self.store1,
            pickup_date=date.today(),
        )
        create_response = self.client.post(self.create_order_url, self.pickup_payload(), format="json")
        order_id = create_response.data["id"]

        response = self.client.post(
            f"/api/v1/orders/{order_id}/test-payment/confirm/",
            {"payment_key": "test_payment_001"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=order_id)
        order.payment.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CONFIRMED)
        self.assertEqual(order.payment_status, Order.PaymentStatus.PAID)
        self.assertEqual(order.payment.status, Payment.Status.PAID)
        self.assertEqual(order.payment.payment_key, "test_payment_001")

    @override_settings(TOSS_PAYMENTS_SECRET_KEY="test_sk_local")
    @patch("apps.orders.services.requests.post")
    def test_confirm_toss_payment_success(self, mock_post):
        """토스 테스트 결제 승인 API 응답이 성공이면 결제 완료 처리한다."""
        mock_response = Mock(ok=True)
        mock_response.json.return_value = {
            "paymentKey": "toss_payment_001",
            "orderId": "ORD_TEST",
            "totalAmount": 10000,
            "status": "DONE",
        }
        mock_post.return_value = mock_response
        CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=1,
            pickup_store=self.store1,
            pickup_date=date.today(),
        )
        create_response = self.client.post(self.create_order_url, self.pickup_payload(), format="json")
        order = Order.objects.get(id=create_response.data["id"])

        response = self.client.post(
            "/api/v1/orders/toss-payment/confirm/",
            {
                "paymentKey": "toss_payment_001",
                "orderId": order.payment.merchant_uid,
                "amount": order.total_price,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        order.payment.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CONFIRMED)
        self.assertEqual(order.payment_status, Order.PaymentStatus.PAID)
        self.assertEqual(order.payment.status, Payment.Status.PAID)
        self.assertEqual(order.payment.provider, Payment.Provider.TOSS_TEST)
        mock_post.assert_called_once()

    @override_settings(TOSS_PAYMENTS_SECRET_KEY="test_sk_local")
    def test_confirm_toss_payment_rejects_amount_mismatch(self):
        """토스 승인 전 서버 주문 금액과 리다이렉트 금액을 비교한다."""
        CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=1,
            pickup_store=self.store1,
            pickup_date=date.today(),
        )
        create_response = self.client.post(self.create_order_url, self.pickup_payload(), format="json")
        order = Order.objects.get(id=create_response.data["id"])

        response = self.client.post(
            "/api/v1/orders/toss-payment/confirm/",
            {
                "paymentKey": "toss_payment_001",
                "orderId": order.payment.merchant_uid,
                "amount": order.total_price - 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        order.refresh_from_db()
        order.payment.refresh_from_db()
        self.assertEqual(order.payment_status, Order.PaymentStatus.FAILED)
        self.assertEqual(order.payment.status, Payment.Status.FAILED)

    def test_create_order_from_cart_uses_selected_item_ids(self):
        """선택한 장바구니 항목만 주문으로 생성한다."""
        selected_item = CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=1,
            pickup_store=self.store1,
            pickup_date=date.today(),
        )
        unselected_item = CartItem.objects.create(
            user=self.user,
            product=self.product2,
            quantity=1,
            pickup_store=self.store1,
            pickup_date=date.today(),
        )

        response = self.client.post(
            self.create_order_url,
            self.pickup_payload(item_ids=[selected_item.id]),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get()
        self.assertEqual(order.total_price, 10000)
        self.assertEqual(order.items.count(), 1)
        self.assertFalse(CartItem.objects.filter(pk=selected_item.pk).exists())
        self.assertTrue(CartItem.objects.filter(pk=unselected_item.pk).exists())

    def test_create_order_from_cart_selection_does_not_include_unselected_package_draft(self):
        """선택 주문 요청에서는 선택하지 않은 커스텀 패키지를 함께 주문하지 않는다."""
        selected_item = CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=1,
            pickup_store=self.store1,
            pickup_date=date.today(),
        )
        draft = CartPackageDraftService.create_draft(
            user=self.user,
            policy_id=self.package_policy.id,
            display_name="선택하지 않은 세트",
            items=[
                {"product_id": str(self.product1.id), "quantity": 1},
                {"product_id": str(self.product2.id), "quantity": 1},
            ],
            pickup_store=self.store1,
            pickup_date=date.today(),
        )

        response = self.client.post(
            self.create_order_url,
            self.pickup_payload(item_ids=[selected_item.id]),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get()
        self.assertEqual(order.total_price, 10000)
        self.assertFalse(OrderCustomPackage.objects.filter(order=order).exists())
        draft.refresh_from_db()
        self.assertEqual(draft.status, draft.Status.DRAFT)

    def test_create_order_from_cart_includes_custom_package_snapshot(self):
        """장바구니 커스텀 패키지는 주문 생성 시 snapshot으로 고정된다."""
        draft = CartPackageDraftService.create_draft(
            user=self.user,
            policy_id=self.package_policy.id,
            display_name="내가 고른 테스트 세트",
            items=[
                {"product_id": str(self.product1.id), "quantity": 1},
                {"product_id": str(self.product2.id), "quantity": 1},
            ],
            pickup_store=self.store1,
            pickup_date=date.today(),
        )

        response = self.client.post(self.create_order_url, self.pickup_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get()
        self.assertEqual(order.total_price, 30000)
        self.assertEqual(OrderCustomPackage.objects.filter(order=order).count(), 1)
        custom_package = order.custom_packages.get()
        self.assertEqual(custom_package.items.count(), 2)
        draft.refresh_from_db()
        self.assertEqual(draft.status, draft.Status.ORDERED)

    def test_create_order_from_empty_cart(self):
        """빈 장바구니에서 주문 생성 시도 테스트"""
        # Given: 사용자의 장바구니가 비어있는 상태

        # When: 주문 생성 API 호출
        response = self.client.post(self.create_order_url)

        # Then: 400 에러와 함께 장바구니가 비었다는 메시지를 반환
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("장바구니가 비어있습니다", response.data["detail"])

    def test_create_order_from_cart_fails_if_no_pickup_info(self):
        """픽업 주문에 주문 단위 픽업 정보가 없으면 실패한다."""
        CartItem.objects.create(user=self.user, product=self.product1, quantity=1)

        response = self.client.post(
            self.create_order_url,
            {"fulfillment_method": Order.FulfillmentMethod.PICKUP},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("픽업 주문은 픽업 매장과 날짜가 필요합니다.", response.data["detail"])
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_from_cart_requires_adult_verification(self):
        """성인 인증을 완료하지 않은 사용자는 주문 생성 불가."""
        self.user.is_adult = False
        self.user.adult_verified_at = None
        self.user.save(update_fields=["is_adult", "adult_verified_at"])
        CartItem.objects.create(
            user=self.user, product=self.product1, quantity=1, pickup_store=self.store1, pickup_date=date.today()
        )

        response = self.client.post(self.create_order_url, self.pickup_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "ADULT_VERIFICATION_REQUIRED")
        self.assertEqual(Order.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_order_from_cart(self):
        """인증되지 않은 사용자의 주문 생성 실패 테스트"""
        # Given: 로그아웃된 클라이언트
        self.client.force_authenticate(user=None)

        # When: 주문 생성 API 호출
        response = self.client.post(self.create_order_url)

        # Then: 403 Forbidden 에러를 반환
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
