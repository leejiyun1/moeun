from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import AdminLoginSerializer, UserSerializer


class AdminLoginView(APIView):
    serializer_class = AdminLoginSerializer
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=AdminLoginSerializer,
        summary="관리자 ID/PW 로그인",
        description="관리자 페이지 접근을 위한 전용 로그인입니다.",
        tags=["admin-auth"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            username=serializer.validated_data["identifier"],
            password=serializer.validated_data["password"],
        )

        if not user or not user.is_admin:
            return Response({"detail": "관리자 계정 정보를 확인해주세요."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "success": True,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_info": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
