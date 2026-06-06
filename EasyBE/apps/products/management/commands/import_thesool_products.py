import argparse
import json
import os
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.products.models import Brewery, Drink, Product, ProductImage


class Command(BaseCommand):
    help = "Import prepared TheSool product payload into Moeun product tables."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--input",
            default="artifacts/data/thesool_import.json",
            help="Prepared Moeun import payload JSON path.",
        )
        parser.add_argument("--commit", action="store_true", help="Persist changes. Default is dry-run.")

    def handle(self, *args: Any, **options: Any) -> None:
        input_path = self._resolve_path(options["input"])
        commit = options["commit"]

        if not input_path.exists():
            raise CommandError(f"input file does not exist: {input_path}")

        payload = json.loads(input_path.read_text(encoding="utf-8"))
        products = payload.get("products", [])
        breweries = payload.get("breweries", [])
        if not isinstance(products, list) or not isinstance(breweries, list):
            raise CommandError("input must contain breweries and products lists")

        result = self._import_payload(products=products, breweries=breweries, commit=commit)
        self.stdout.write(
            self.style.SUCCESS(
                f"{'imported' if commit else 'dry-run'} "
                f"breweries={result['breweries']}, "
                f"drinks={result['drinks']}, "
                f"products={result['products']}, "
                f"images={result['images']}"
            )
        )

    @transaction.atomic
    def _import_payload(
        self,
        *,
        products: list[dict[str, Any]],
        breweries: list[dict[str, Any]],
        commit: bool,
    ) -> dict[str, int]:
        brewery_by_key = {}
        result = {"breweries": 0, "drinks": 0, "products": 0, "images": 0}

        for brewery_data in breweries:
            brewery, _ = Brewery.objects.update_or_create(
                name=brewery_data["name"],
                address=brewery_data.get("address") or None,
                defaults={
                    "region": brewery_data.get("region") or None,
                    "phone": brewery_data.get("phone") or None,
                    "description": brewery_data.get("description") or None,
                    "image_url": brewery_data.get("image_url") or None,
                    "homepage_url": brewery_data.get("homepage_url") or None,
                    "is_active": brewery_data.get("is_active", True),
                },
            )
            brewery_by_key[brewery_data["client_key"]] = brewery
            result["breweries"] += 1

        for item in products:
            brewery = brewery_by_key[item["brewery_client_key"]]
            drink_data = item["drink"]
            product_data = item["product"]

            drink, _ = Drink.objects.update_or_create(
                brewery=brewery,
                name=drink_data["name"],
                alcohol_type=drink_data["alcohol_type"],
                abv=drink_data["abv"],
                volume_ml=drink_data["volume_ml"],
                defaults={
                    "ingredients": drink_data["ingredients"],
                    "food_pairing": drink_data.get("food_pairing") or "",
                    "sweetness_level": drink_data["sweetness_level"],
                    "acidity_level": drink_data["acidity_level"],
                    "body_level": drink_data["body_level"],
                    "carbonation_level": drink_data["carbonation_level"],
                    "bitterness_level": drink_data["bitterness_level"],
                    "aroma_level": drink_data["aroma_level"],
                },
            )
            result["drinks"] += 1

            product, _ = Product.objects.update_or_create(
                drink=drink,
                defaults={
                    "price": product_data["price"],
                    "original_price": product_data.get("original_price"),
                    "discount": product_data.get("discount"),
                    "description": product_data["description"],
                    "description_image_url": product_data["description_image_url"],
                    "is_tasting_available": product_data.get("is_tasting_available", False),
                    "status": product_data["status"],
                },
            )
            result["products"] += 1

            product.images.all().delete()
            ProductImage.objects.bulk_create(
                [
                    ProductImage(
                        product=product,
                        image_url=image["image_url"],
                        is_main=image.get("is_main", False),
                    )
                    for image in item["images"]
                ]
            )
            result["images"] += len(item["images"])

        if not commit:
            transaction.set_rollback(True)

        return result

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
