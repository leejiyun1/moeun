# apps/users/utils/social_auth.py

from typing import Any, Dict, Tuple

from django.db import transaction

from apps.users.models import SocialAccount, User

from ..utils.nickname_generator import NicknameGenerator


class SocialAuthService:
    @staticmethod
    @transaction.atomic
    def authenticate_social_user(provider: str, provider_id: str, user_info: Dict[str, Any]) -> Tuple[User, str]:
        """
        소셜 로그인 인증. 성인 인증은 주류 주문/시음 신청 직전에 확인한다.
        """
        email = user_info.get("email")

        # 1. 기존 소셜 계정 확인
        try:
            social_account = SocialAccount.objects.get(provider=provider, provider_id=provider_id)
            user = social_account.user

            if user.is_adult:
                return user, "existing_verified"
            return user, "existing_unverified"

        except SocialAccount.DoesNotExist:
            pass

        # 2. 동일한 이메일의 기존 사용자 확인
        existing_user = None
        if email:
            existing_user = User.objects.get_by_email(email)

        # 3-1. 기존 사용자가 있다면 새 소셜 계정 연결
        if existing_user:
            SocialAccount.objects.create(
                user=existing_user, provider=provider, provider_id=provider_id, provider_email=email
            )

            if existing_user.is_adult:
                return existing_user, "linked_verified"
            return existing_user, "linked_unverified"

        # 3-2. 새 사용자도 로그인은 허용하고, 주류 신청 직전에 성인 인증을 요구한다.
        unique_nickname = NicknameGenerator.generate_unique_nickname(User)
        user = User.objects.create_user(nickname=unique_nickname, email=email)
        SocialAccount.objects.create(user=user, provider=provider, provider_id=provider_id, provider_email=email)
        return user, "new_unverified"

    @staticmethod
    def link_social_account(user, provider, provider_id, provider_email=None):
        """
        기존 사용자에게 소셜 계정 연결
        """
        # 이미 연결된 소셜 계정인지 확인
        if SocialAccount.objects.filter(provider=provider, provider_id=provider_id).exists():
            raise ValueError("이미 다른 계정에 연결된 소셜 계정입니다.")

        social_account = SocialAccount.objects.create(
            user=user, provider=provider, provider_id=provider_id, provider_email=provider_email
        )

        return social_account
