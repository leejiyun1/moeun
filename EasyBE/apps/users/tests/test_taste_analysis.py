# apps/users/tests/test_taste_analysis.py

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.taste_test.models import PreferenceTestResult
from apps.users.models import PreferTasteProfile
from apps.users.utils.taste_analysis import TasteAnalysisService

User = get_user_model()


class TasteAnalysisServiceTest(TestCase):
    """TasteAnalysisService 테스트 - 실제 객체 사용"""

    def setUp(self):
        """테스트 데이터 설정"""
        # 사용자 생성
        self.user = User.objects.create_user(nickname="testuser", email="test@example.com")

        # 취향 테스트 결과 생성
        self.test_result = PreferenceTestResult.objects.create(
            user=self.user, prefer_taste=PreferenceTestResult.PreferTaste.SWEET_FRUIT, answers={"Q1": "A", "Q2": "B"}
        )

        # 취향 프로필 생성
        self.taste_profile = PreferTasteProfile.objects.create(
            user=self.user,
            sweetness_level=Decimal("4.0"),
            acidity_level=Decimal("2.5"),
            body_level=Decimal("2.0"),
            carbonation_level=Decimal("2.0"),
            bitterness_level=Decimal("1.5"),
            aroma_level=Decimal("4.0"),
            total_reviews_count=0,
        )

    def test_generate_analysis_without_learning_data(self):
        """후기 분석 데이터가 없는 경우 분석 생성 테스트"""
        analysis = TasteAnalysisService.generate_analysis(self.taste_profile)

        self.assertIn("취향 테스트 결과를 기준으로", analysis)

    def test_generate_analysis_with_few_learning_data(self):
        """후기 분석 데이터가 적은 경우 분석 생성 테스트"""
        self.taste_profile.total_reviews_count = 2
        self.taste_profile.save()

        analysis = TasteAnalysisService.generate_analysis(self.taste_profile)

        self.assertIn("아직 후기 분석 데이터가 적어서", analysis)
        self.assertIn("대략적인 취향만", analysis)

    def test_generate_analysis_with_many_learning_data(self):
        """후기 분석 데이터가 많은 경우 분석 생성 테스트"""
        self.taste_profile.total_reviews_count = 15
        self.taste_profile.sweetness_level = Decimal("4.5")  # 높은 선호도
        self.taste_profile.bitterness_level = Decimal("1.0")  # 낮은 선호도
        self.taste_profile.save()

        analysis = TasteAnalysisService.generate_analysis(self.taste_profile)

        self.assertIn("15개의 후기 분석 결과를 반영", analysis)
        self.assertIn("단맛", analysis)  # 높은 선호도 언급
        self.assertIn("쓴맛", analysis)  # 낮은 선호도 언급

    def test_get_recommendation_sweet_fruit_pattern(self):
        """달콤과일파 패턴 추천 테스트"""
        scores = {
            "sweetness_level": 4.5,
            "acidity_level": 3.0,
            "body_level": 2.0,
            "carbonation_level": 2.0,
            "bitterness_level": 1.0,
            "aroma_level": 4.5,
        }

        recommendation = TasteAnalysisService._get_recommendation(scores, ["단맛", "향"], ["쓴맛"])

        self.assertIn("과일의 달콤함", recommendation)
        self.assertIn("약주나 리큐르", recommendation)
