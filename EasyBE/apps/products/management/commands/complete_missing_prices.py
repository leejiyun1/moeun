import argparse
import json
import os
from pathlib import Path
from statistics import median
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import Product


class Command(BaseCommand):
    help = "Fill remaining zero product prices from researched price distribution."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--output", default="artifacts/data/price_completion_report.json")
        parser.add_argument("--commit", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        products = list(Product.objects.select_related("drink").filter(drink__isnull=False))
        priced = [product for product in products if product.price > 0]
        missing = [product for product in products if product.price == 0]

        if not priced:
            self.stdout.write(self.style.WARNING("no researched prices available"))
            return

        exact_groups = self._build_groups(priced, exact=True)
        broad_groups = self._build_groups(priced, exact=False)
        type_groups: dict[str, list[int]] = {}
        for product in priced:
            type_groups.setdefault(product.drink.alcohol_type, []).append(product.price)

        global_median = int(median(product.price for product in priced))
        updates = []
        records = []

        for product in missing:
            price, basis = self._estimate_price(
                product=product,
                exact_groups=exact_groups,
                broad_groups=broad_groups,
                type_groups=type_groups,
                global_median=global_median,
            )
            product.price = price
            product.original_price = None
            product.discount = None
            updates.append(product)
            records.append(
                {
                    "product_id": str(product.id),
                    "name": product.drink.name,
                    "alcohol_type": product.drink.alcohol_type,
                    "volume_ml": product.drink.volume_ml,
                    "abv": str(product.drink.abv),
                    "price": price,
                    "basis": basis,
                }
            )

        if options["commit"] and updates:
            with transaction.atomic():
                Product.objects.bulk_update(updates, ["price", "original_price", "discount"])

        output_path = self._resolve_path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                {
                    "schema": "moeun.products.price_completion.v1",
                    "commit": options["commit"],
                    "researched_count": len(priced),
                    "completed_count": len(records),
                    "records": records,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"completed prices: researched={len(priced)}, completed={len(records)}, output={output_path}"
            )
        )

    def _build_groups(self, products: list[Product], *, exact: bool) -> dict[tuple[Any, ...], list[int]]:
        groups: dict[tuple[Any, ...], list[int]] = {}
        for product in products:
            drink = product.drink
            key = (
                drink.alcohol_type,
                self._volume_band(drink.volume_ml, exact=exact),
                self._abv_band(float(drink.abv), exact=exact),
            )
            groups.setdefault(key, []).append(product.price)
        return groups

    def _estimate_price(
        self,
        *,
        product: Product,
        exact_groups: dict[tuple[Any, ...], list[int]],
        broad_groups: dict[tuple[Any, ...], list[int]],
        type_groups: dict[str, list[int]],
        global_median: int,
    ) -> tuple[int, str]:
        drink = product.drink
        exact_key = (drink.alcohol_type, self._volume_band(drink.volume_ml, exact=True), self._abv_band(float(drink.abv), exact=True))
        broad_key = (drink.alcohol_type, self._volume_band(drink.volume_ml, exact=False), self._abv_band(float(drink.abv), exact=False))

        if exact_key in exact_groups and len(exact_groups[exact_key]) >= 2:
            return self._round_price(median(exact_groups[exact_key])), f"median_exact:{exact_key}"
        if broad_key in broad_groups:
            return self._round_price(median(broad_groups[broad_key])), f"median_broad:{broad_key}"
        if drink.alcohol_type in type_groups:
            return self._round_price(median(type_groups[drink.alcohol_type])), f"median_type:{drink.alcohol_type}"
        return self._round_price(global_median), "median_global"

    def _volume_band(self, volume_ml: int, *, exact: bool) -> str:
        if exact:
            if volume_ml <= 375:
                return "small"
            if volume_ml <= 500:
                return "medium"
            if volume_ml <= 750:
                return "standard"
            return "large"
        if volume_ml <= 500:
            return "small_medium"
        if volume_ml <= 900:
            return "standard"
        return "large"

    def _abv_band(self, abv: float, *, exact: bool) -> str:
        if exact:
            if abv < 8:
                return "low"
            if abv < 16:
                return "mid"
            if abv < 25:
                return "high"
            return "spirit"
        if abv < 16:
            return "low_mid"
        return "high_spirit"

    def _round_price(self, value: float) -> int:
        return max(1000, int(round(value / 100) * 100))

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
