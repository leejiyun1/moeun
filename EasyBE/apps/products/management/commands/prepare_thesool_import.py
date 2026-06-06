import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError


REGION_ALIASES = {
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원도",
    "충북": "충청북도",
    "충청북도": "충청북도",
    "충남": "충청남도",
    "충청남도": "충청남도",
    "전북": "전라북도",
    "전라북도": "전라북도",
    "전남": "전라남도",
    "전라남도": "전라남도",
    "경북": "경상북도",
    "경상북도": "경상북도",
    "경남": "경상남도",
    "경상남도": "경상남도",
    "제주": "제주특별자치도",
    "제주특별자치도": "제주특별자치도",
}

TASTE_FIELDS = (
    "sweetness_level",
    "acidity_level",
    "body_level",
    "carbonation_level",
    "bitterness_level",
    "aroma_level",
)


class Command(BaseCommand):
    help = "Convert collected TheSool JSON into a Moeun import payload shape."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--input",
            default="artifacts/data/thesool_products.json",
            help="Collected TheSool JSON path.",
        )
        parser.add_argument(
            "--output",
            default="artifacts/data/thesool_import.json",
            help="Moeun import payload JSON path.",
        )
        parser.add_argument("--default-price", type=int, default=0)
        parser.add_argument(
            "--media-base-url",
            default="http://localhost/media",
            help="Base URL used for locally served product image URLs.",
        )
        parser.add_argument(
            "--status",
            choices=("ACTIVE", "INACTIVE", "OUT_OF_STOCK"),
            default="INACTIVE",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        input_path = self._resolve_path(options["input"])
        output_path = self._resolve_path(options["output"])

        if not input_path.exists():
            raise CommandError(f"input file does not exist: {input_path}")

        source = json.loads(input_path.read_text(encoding="utf-8"))
        products = source.get("products", [])
        if not isinstance(products, list):
            raise CommandError("input products must be a list")

        payload = self._build_payload(
            products,
            default_price=options["default_price"],
            status=options["status"],
            media_base_url=options["media_base_url"],
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.stdout.write(
            self.style.SUCCESS(
                "prepared "
                f"{len(payload['products'])} products, "
                f"{len(payload['breweries'])} breweries -> {output_path}"
            )
        )

    def _build_payload(
        self,
        products: list[dict[str, Any]],
        *,
        default_price: int,
        status: str,
        media_base_url: str,
    ) -> dict[str, Any]:
        breweries_by_key: dict[str, dict[str, Any]] = {}
        import_products = []
        skipped = []

        for item in products:
            brewery = item["brewery"]
            drink = item["drink"]
            product = item["product"]
            image = item["image"]

            brewery_key = self._build_brewery_key(brewery)
            if brewery_key not in breweries_by_key:
                breweries_by_key[brewery_key] = {
                    "client_key": brewery_key,
                    "name": brewery["name"],
                    "region": self._normalize_region(brewery.get("region") or brewery.get("address") or ""),
                    "address": brewery.get("address") or "",
                    "phone": self._normalize_phone(brewery.get("phone") or ""),
                    "description": "",
                    "image_url": "",
                    "homepage_url": brewery.get("homepage_url") or "",
                    "is_active": True,
                }

            taste_profile = drink.get("taste_profile") or {}
            missing_taste = [field for field in TASTE_FIELDS if taste_profile.get(field) is None]
            if missing_taste:
                skipped.append(
                    {
                        "source_id": item["source_id"],
                        "name": item["name"],
                        "reason": f"missing taste fields: {', '.join(missing_taste)}",
                    }
                )
                continue

            storage_key = self._normalize_storage_key(image["storage_key"], image["code_name"])
            image_url = self._build_media_url(media_base_url, storage_key)
            import_products.append(
                {
                    "client_key": self._build_product_key(item["source_id"], item["name"]),
                    "brewery_client_key": brewery_key,
                    "source": {
                        "provider": item.get("source_name") or "TheSool",
                        "source_id": item["source_id"],
                        "source_url": item.get("source_url") or product.get("source_url") or "",
                        "content_hash": item.get("raw", {}).get("content_hash") or "",
                    },
                    "drink": {
                        "name": drink["name"],
                        "ingredients": drink["ingredients"],
                        "alcohol_type": drink["alcohol_type"],
                        "abv": float(drink["abv"]),
                        "volume_ml": int(drink["volume_ml"]),
                        "food_pairing": drink.get("food_pairing") or "",
                        "sweetness_level": self._taste_value(taste_profile["sweetness_level"]),
                        "acidity_level": self._taste_value(taste_profile["acidity_level"]),
                        "body_level": self._taste_value(taste_profile["body_level"]),
                        "carbonation_level": self._taste_value(taste_profile["carbonation_level"]),
                        "bitterness_level": self._taste_value(taste_profile["bitterness_level"]),
                        "aroma_level": self._taste_value(taste_profile["aroma_level"]),
                        "taste_meta": {
                            "confidence": taste_profile.get("confidence"),
                            "needs_review": taste_profile.get("needs_review", True),
                            "note": taste_profile.get("inference_note") or "TheSool keyword-based draft.",
                        },
                    },
                    "product": {
                        "price": default_price,
                        "original_price": None,
                        "discount": None,
                        "description": product["description"],
                        "description_image_url": image_url,
                        "is_tasting_available": False,
                        "status": status,
                    },
                    "images": [
                        {
                            "image_url": image_url,
                            "is_main": True,
                            "code_name": image["code_name"],
                            "storage_key": storage_key,
                        }
                    ],
                    "raw": {
                        "alcohol_type_label": drink.get("alcohol_type_label") or "",
                        "awards": item.get("raw", {}).get("awards") or "",
                        "extra": item.get("raw", {}).get("extra") or "",
                        "labels": item.get("raw", {}).get("labels") or [],
                    },
                }
            )

        return {
            "schema": "moeun.products.import.v1",
            "defaults": {
                "price": default_price,
                "status": status,
                "is_tasting_available": False,
                "product_type": "individual",
            },
            "counts": {
                "source_products": len(products),
                "breweries": len(breweries_by_key),
                "products": len(import_products),
                "skipped": len(skipped),
            },
            "breweries": sorted(breweries_by_key.values(), key=lambda value: value["client_key"]),
            "products": import_products,
            "skipped": skipped,
        }

    def _build_brewery_key(self, brewery: dict[str, Any]) -> str:
        seed = "|".join(
            [
                brewery.get("name") or "",
                brewery.get("address") or "",
                brewery.get("phone") or "",
            ]
        )
        return f"brewery-{self._slug_hash(seed)}"

    def _build_product_key(self, source_id: str, name: str) -> str:
        return f"product-thesool-{source_id.lower()}-{self._slug_hash(name)[:8]}"

    def _slug_hash(self, value: str) -> str:
        digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]
        return digest

    def _normalize_region(self, value: str) -> str:
        compact = re.sub(r"^\(\d+\)", "", value).strip()
        first_token = compact.split(" ", 1)[0] if compact else ""
        return REGION_ALIASES.get(first_token, first_token[:30])

    def _normalize_phone(self, value: str) -> str:
        value = value.strip()
        if "-" in value:
            return value
        digits = re.sub(r"\D", "", value)
        if len(digits) == 10 and digits.startswith("02"):
            return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        if len(digits) == 11:
            return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        return value

    def _taste_value(self, value: Any) -> float:
        return max(0.0, min(5.0, round(float(value), 1)))

    def _normalize_storage_key(self, storage_key: str, code_name: str) -> str:
        parts = storage_key.split("/")
        if len(parts) >= 4:
            return storage_key

        category = "etc"
        if code_name.startswith("thesool-"):
            name_parts = code_name.split("-")
            if len(name_parts) > 1:
                category = name_parts[1]
        return f"products/thesool/{category}/{code_name}"

    def _build_media_url(self, media_base_url: str, storage_key: str) -> str:
        return f"{media_base_url.rstrip('/')}/{storage_key.lstrip('/')}"

    def _resolve_path(self, value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path

        artifacts_dir = os.environ.get("ARTIFACTS_DIR")
        if artifacts_dir:
            parts = path.parts
            if parts and parts[0] == "artifacts":
                path = Path(*parts[1:])
            return Path(artifacts_dir) / path

        return Path.cwd() / path
