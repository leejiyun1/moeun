import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone


class ProductImageStorage:
    """상품 이미지 저장소 어댑터.

    현재는 Django default storage에 저장하고 URL을 반환한다. S3/NCP 전환 시
    이 클래스 내부 구현만 교체하면 모델과 serializer 계약은 유지된다.
    """

    ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    MAX_FILE_SIZE = 10 * 1024 * 1024

    @classmethod
    def save_main_image(cls, image_file: UploadedFile) -> str:
        return cls._save(image_file, "main")

    @classmethod
    def save_description_image(cls, image_file: UploadedFile) -> str:
        return cls._save(image_file, "description")

    @classmethod
    def _save(cls, image_file: UploadedFile, image_role: str) -> str:
        cls._validate(image_file)
        now = timezone.now()
        extension = cls._get_extension(image_file.name)
        path = f"products/{now:%Y/%m}/{image_role}-{uuid.uuid4().hex}{extension}"
        saved_path = default_storage.save(path, image_file)
        return cls._build_url(saved_path)

    @classmethod
    def _validate(cls, image_file: UploadedFile) -> None:
        content_type = getattr(image_file, "content_type", "")
        if content_type not in cls.ALLOWED_CONTENT_TYPES:
            raise ValueError("상품 이미지는 jpg, png, webp, gif 파일만 업로드할 수 있습니다.")
        if image_file.size > cls.MAX_FILE_SIZE:
            raise ValueError("상품 이미지는 10MB 이하만 업로드할 수 있습니다.")

    @staticmethod
    def _get_extension(filename: str) -> str:
        extension = Path(filename).suffix.lower()
        return extension if extension in {".jpg", ".jpeg", ".png", ".webp", ".gif"} else ".jpg"

    @staticmethod
    def _build_url(path: str) -> str:
        media_url = getattr(settings, "MEDIA_URL", "/media/")
        relative_url = f"{media_url.rstrip('/')}/{path.lstrip('/')}"
        base_url = getattr(settings, "BASE_URL", "").rstrip("/")
        return f"{base_url}/{relative_url.lstrip('/')}" if base_url else relative_url
