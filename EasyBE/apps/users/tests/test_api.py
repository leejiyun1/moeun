# apps/users/tests/test_api.py

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import PreferTasteProfile

User = get_user_model()


class TasteProfileAPITest(TestCase):
    """취향 프로필 API 테스트"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(nickname="testuser", email="test@example.com")

        # JWT 토큰 생성 및 인증
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.url = reverse("users:v1:taste_profile")

    def test_get_taste_profile_success(self):
        """취향 프로필 조회 성공 테스트"""
        response = self.client.get(self.url)

        # 성공 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 프로필 자동 생성 확인
        self.assertTrue(PreferTasteProfile.objects.filter(user=self.user).exists())

        # 응답 데이터 구조 확인
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("taste_scores", data)
        self.assertIn("description", data)

        # taste_scores 필드들 확인
        taste_scores = data["taste_scores"]
        expected_fields = [
            "sweetness_level",
            "acidity_level",
            "body_level",
            "carbonation_level",
            "bitterness_level",
            "aroma_level",
        ]
        for field in expected_fields:
            self.assertIn(field, taste_scores)
            self.assertIsInstance(taste_scores[field], float)

    def test_get_taste_profile_unauthorized(self):
        """비인증 사용자 접근 테스트"""
        self.client.credentials()  # 인증 해제

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_taste_profile_with_reviews(self):
        """리뷰가 있는 경우 분석 설명 테스트"""
        # 프로필 생성 및 리뷰 수 설정
        profile = PreferTasteProfile.objects.create(
            user=self.user, sweetness_level=Decimal("4.5"), acidity_level=Decimal("3.5"), total_reviews_count=5
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        # 분석 설명이 생성되었는지 확인
        self.assertIsNotNone(data["description"])
        self.assertNotEqual(data["description"], "")


class AdminLoginAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("users:v1:admin_login")
        self.admin = User.objects.create_user(
            nickname="admin@test.com",
            email="admin@test.com",
            role=User.Role.ADMIN,
        )
        self.admin.set_password("test1234")
        self.admin.save(update_fields=["password"])
        self.user = User.objects.create_user(nickname="normal", email="normal@test.com")
        self.user.set_password("test1234")
        self.user.save(update_fields=["password"])

    def test_admin_login_success(self):
        response = self.client.post(
            self.url,
            {"identifier": "admin@test.com", "password": "test1234"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user_info"]["role"], User.Role.ADMIN)

    def test_admin_login_rejects_normal_user(self):
        response = self.client.post(
            self.url,
            {"identifier": "normal", "password": "test1234"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_login_rejects_invalid_password(self):
        response = self.client.post(
            self.url,
            {"identifier": "admin@test.com", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
