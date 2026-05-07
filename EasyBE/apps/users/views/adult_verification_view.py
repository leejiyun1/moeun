from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import DemoAdultVerificationSerializer, UserSerializer


class DemoAdultVerificationView(APIView):
    """데모 성인 인증 처리.

    외부 본인인증 provider 연동 전까지 개발/포트폴리오 환경에서만 사용한다.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = DemoAdultVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        birth_date = serializer.validated_data["birth_date"]
        if not self._is_legal_adult(birth_date):
            return Response({"detail": "만 19세 이상만 신청할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        request.user.verify_adult()
        return Response({"success": True, "user_info": UserSerializer(request.user).data}, status=status.HTTP_200_OK)

    @staticmethod
    def _is_legal_adult(birth_date):
        from django.utils import timezone

        today = timezone.localdate()
        return today.year - birth_date.year >= 19
