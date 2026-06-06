# apps/users/views/google_view.py
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.utils.jwt import JWTService
from apps.users.utils.social_auth import SocialAuthService

from ..serializers import GoogleLoginSerializer, UserSerializer
from ..social_login.google_service import GoogleService
from ..utils.cache_oauth_state import OAuthStateService


class GoogleLoginView(APIView):
    """
    구글 소셜 로그인 API
    POST /api/v1/auth/login/google/
    """

    serializer_class = GoogleLoginSerializer

    def post(self, request: Request) -> Response:
        # 0. 요청 데이터 검증
        serializer = GoogleLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        authorization_code = serializer.validated_data["code"]
        redirect_uri = serializer.validated_data.get("redirect_uri")

        try:
            # 1. 구글에서 access token 획득
            token_data = GoogleService.get_access_token(authorization_code, redirect_uri)
            access_token = token_data["access_token"]

            # 2. access token으로 구글 사용자 정보 획득
            google_user_data = GoogleService.get_user_info(access_token)

            # 3. 구글 데이터 파싱
            google_id = str(google_user_data["id"])
            email = google_user_data.get("email")

            # 4. 사용자 인증. 성인 인증은 주문/시음 신청 직전에 확인한다.
            user, auth_status = SocialAuthService.authenticate_social_user(
                provider="GOOGLE", provider_id=google_id, user_info={"email": email}
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
