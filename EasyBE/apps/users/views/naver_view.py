# apps/users/views/naver_view.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.utils.jwt import JWTService
from apps.users.utils.social_auth import SocialAuthService

from ..serializers import NaverLoginSerializer, UserSerializer
from ..social_login.naver_service import NaverService
from ..utils.cache_oauth_state import OAuthStateService


class NaverLoginView(APIView):
    """
    네이버 소셜 로그인 API
    POST /api/v1/auth/login/naver/
    """

    serializer_class = NaverLoginSerializer

    def post(self, request):
        # 0. 요청 데이터 검증
        serializer = NaverLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        authorization_code = serializer.validated_data["code"]
        state = serializer.validated_data["state"]

        try:
            # 1. 네이버에서 access token 획득
            token_data = NaverService.get_access_token(authorization_code, state)
            access_token = token_data["access_token"]

            # 2. access token으로 네이버 사용자 정보 획득
            naver_user_data = NaverService.get_user_info(access_token)

            # 3. 네이버 데이터 파싱
            if naver_user_data.get("resultcode") != "00":
                raise Exception(f"네이버 사용자 정보 조회 실패: {naver_user_data.get('message')}")

            response_data = naver_user_data.get("response", {})
            naver_id = response_data.get("id")
            email = response_data.get("email")

            if not naver_id:
                raise Exception("네이버 ID를 가져올 수 없습니다.")

            # 4. 사용자 인증. 성인 인증은 주문/시음 신청 직전에 확인한다.
            user, auth_status = SocialAuthService.authenticate_social_user(
                provider="NAVER", provider_id=naver_id, user_info={"email": email}
            )

            # 5. 로그인은 완료하고, 주류 주문/시음 신청 직전에 성인 인증을 요구한다.
            tokens = JWTService.create_tokens_for_user(user)
            return Response(
                {
                    "success": True,
                    "access": tokens["access_token"],
                    "refresh": tokens["refresh_token"],
                    "user_info": UserSerializer(user).data,
                    "auth_type": auth_status,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"로그인 처리 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
