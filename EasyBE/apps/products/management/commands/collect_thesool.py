import argparse
import hashlib
import html
import json
import os
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from django.core.management.base import BaseCommand, CommandError


BASE_URL = "https://thesool.com"
LIST_PATH = "/front/find/M000000082/list.do"
VIEW_PATH = "/front/find/M000000082/view.do"
PRODUCT_IMAGE_PATH = "/common/imageView.do?targetId={product_id}&targetNm=PRODUCT"

ALCOHOL_TYPE_MAP = {
    "탁주": "MAKGEOLLI",
    "막걸리": "MAKGEOLLI",
    "약주": "YAKJU",
    "청주": "CHEONGJU",
    "과실주": "FRUIT_WINE",
    "증류주": "SOJU",
}

IMAGE_CATEGORY_CODE = {
    "MAKGEOLLI": "takju",
    "YAKJU": "yakju",
    "CHEONGJU": "cheongju",
    "FRUIT_WINE": "fruit",
    "SOJU": "soju",
}

REGION_PREFIXES = (
    "서울특별시",
    "부산광역시",
    "대구광역시",
    "인천광역시",
    "광주광역시",
    "대전광역시",
    "울산광역시",
    "세종특별자치시",
    "경기도",
    "강원도",
    "충청북도",
    "충청남도",
    "전라북도",
    "전라남도",
    "경상북도",
    "경상남도",
    "제주특별자치도",
)


@dataclass
class TheSoolProduct:
    source_id: str
    source_name: str
    source_url: str
    name: str
    brewery: dict[str, Any]
    drink: dict[str, Any]
    product: dict[str, Any]
    image: dict[str, Any]
    raw: dict[str, Any]


class Command(BaseCommand):
    help = "Collect TheSool product data into a DB-friendly JSON file."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--start-page", type=int, default=1)
        parser.add_argument("--max-pages", type=int, default=126)
        parser.add_argument(
            "--strategy",
            choices=("list", "id-scan"),
            default="list",
            help="list follows pageIndex. id-scan checks PR00000001.. range and is more stable for TheSool.",
        )
        parser.add_argument("--id-start", type=int, default=1)
        parser.add_argument("--id-end", type=int, default=1500)
        parser.add_argument("--delay", type=float, default=0.15)
        parser.add_argument(
            "--output",
            default="artifacts/data/thesool_products.json",
            help="Output JSON path relative to the repository root.",
        )
        parser.add_argument(
            "--skip-detail",
            action="store_true",
            help="Use list page data only. Faster, but omits food pairing and brewery homepage.",
        )
        parser.add_argument(
            "--drop-incomplete",
            action="store_true",
            help="Exclude products missing core import fields such as description, food pairing, volume, or ABV.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        start_page = options["start_page"]
        max_pages = options["max_pages"]
        delay = options["delay"]
        output_path = self._resolve_output_path(options["output"])
        skip_detail = options["skip_detail"]
        strategy = options["strategy"]

        if start_page < 1 or max_pages < 1:
            raise CommandError("start-page and max-pages must be positive integers.")

        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "MoeunDataCollector/1.0 (+https://thesool.com)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )

        if strategy == "id-scan":
            products = self._collect_by_id_scan(
                session=session,
                id_start=options["id_start"],
                id_end=options["id_end"],
                delay=delay,
            )
        else:
            products = self._collect_by_list_pages(
                session=session,
                start_page=start_page,
                max_pages=max_pages,
                delay=delay,
                skip_detail=skip_detail,
            )

        if options["drop_incomplete"]:
            before_count = len(products)
            products = [product for product in products if self._is_complete_product(product)]
            self.stdout.write(f"dropped incomplete products: {before_count - len(products)}")

        payload = {
            "source": {
                "name": "TheSool",
                "list_url": urljoin(BASE_URL, LIST_PATH),
                "collected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "strategy": strategy,
                "pages": {"start": start_page, "end": start_page + max_pages - 1},
                "id_scan": {"start": options["id_start"], "end": options["id_end"]},
            },
            "schema": {
                "brewery": ["name", "region", "address", "phone", "homepage_url"],
                "drink": [
                    "name",
                    "ingredients",
                    "alcohol_type",
                    "abv",
                    "volume_ml",
                    "food_pairing",
                    "taste_profile",
                ],
                "product": ["description", "price", "source_name", "source_url", "status"],
                "image": ["source_url", "code_name", "storage_key"],
            },
            "count": len(products),
            "products": [asdict(product) for product in products],
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.stdout.write(self.style.SUCCESS(f"collected {len(products)} products -> {output_path}"))

    def _is_complete_product(self, product: TheSoolProduct) -> bool:
        return all(
            [
                product.name,
                product.brewery["name"],
                product.drink["ingredients"],
                product.drink["abv"] is not None,
                product.drink["volume_ml"] is not None,
                product.drink["food_pairing"],
                product.product["description"],
                product.image["source_url"],
            ]
        )

    def _collect_by_list_pages(
        self,
        *,
        session: requests.Session,
        start_page: int,
        max_pages: int,
        delay: float,
        skip_detail: bool,
    ) -> list[TheSoolProduct]:
        products: list[TheSoolProduct] = []
        seen_ids: set[str] = set()
        end_page = start_page + max_pages - 1

        for page in range(start_page, end_page + 1):
            list_html = self._fetch(
                session,
                LIST_PATH,
                params={"pageIndex": page},
            )
            list_items = self._parse_list_items(list_html)
            if not list_items:
                self.stdout.write(self.style.WARNING(f"page {page}: no items found, stopping."))
                break

            self.stdout.write(f"page {page}: {len(list_items)} items")
            for item in list_items:
                source_id = item["source_id"]
                if source_id in seen_ids:
                    continue
                seen_ids.add(source_id)

                detail = item
                if not skip_detail:
                    detail_html = self._fetch(
                        session,
                        VIEW_PATH,
                        params={"productId": source_id},
                    )
                    detail = {**item, **self._parse_detail(detail_html, source_id)}
                    time.sleep(delay)

                products.append(self._normalize_product(detail))

            time.sleep(delay)

        return products

    def _collect_by_id_scan(
        self,
        *,
        session: requests.Session,
        id_start: int,
        id_end: int,
        delay: float,
    ) -> list[TheSoolProduct]:
        products: list[TheSoolProduct] = []
        total = id_end - id_start + 1

        for index, numeric_id in enumerate(range(id_start, id_end + 1), start=1):
            source_id = f"PR{numeric_id:08d}"
            try:
                detail_html = self._fetch(
                    session,
                    VIEW_PATH,
                    params={"productId": source_id},
                )
            except requests.HTTPError:
                continue

            detail = self._parse_detail(detail_html, source_id)
            if not detail.get("name"):
                continue

            products.append(self._normalize_product(detail))
            if len(products) % 100 == 0:
                self.stdout.write(f"id scan {index}/{total}: collected {len(products)}")
            time.sleep(delay)

        return products

    def _fetch(self, session: requests.Session, path: str, params: dict[str, Any] | None = None) -> str:
        response = session.get(urljoin(BASE_URL, path), params=params, timeout=20)
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.text

    def _parse_list_items(self, page_html: str) -> list[dict[str, Any]]:
        items = []
        for block in re.findall(r'<li class="item">([\s\S]*?)</li>\s*</ul>\s*</dd>\s*</dl>\s*</li>', page_html):
            source_id = self._first_match(block, r"move\('([^']+)'\)")
            if not source_id:
                continue
            items.append(
                {
                    "source_id": source_id,
                    "name": self._clean(self._first_match(block, r'<div class="name"[^>]*>([\s\S]*?)</div>')),
                    "brewery_name": self._info_value(block, "제조사"),
                    "ingredients": self._info_value(block, "주원료"),
                    "spec": self._info_value(block, "규격/도수"),
                    "description": self._info_value(block, "제품특징"),
                    "labels": re.findall(r'alt="([^"]+)"', block),
                }
            )
        return items

    def _parse_detail(self, page_html: str, source_id: str) -> dict[str, Any]:
        return {
            "source_id": source_id,
            "name": self._clean(self._first_match(page_html, r'<dt class="subject">([\s\S]*?)</dt>')),
            "category": self._detail_value(page_html, "종류"),
            "ingredients": self._detail_value(page_html, "원재료"),
            "abv_text": self._detail_value(page_html, "알콜도수"),
            "volume_text": self._detail_value(page_html, "용량"),
            "awards": self._detail_value(page_html, "수상내역"),
            "extra": self._detail_value(page_html, "기타"),
            "description": self._section_text(page_html, "intro"),
            "food_pairing": self._section_text(page_html, "food"),
            "brewery_name": self._place_value(page_html, "양조장명"),
            "brewery_address": self._place_value(page_html, "주소"),
            "brewery_homepage_url": self._place_homepage(page_html),
            "brewery_phone": self._place_phone(page_html),
            "labels": re.findall(r'alt="([^"]+)"', page_html),
        }

    def _normalize_product(self, data: dict[str, Any]) -> TheSoolProduct:
        source_id = data["source_id"]
        name = data.get("name") or source_id
        category = data.get("category") or ""
        alcohol_type = self._map_alcohol_type(category, name)
        volume_ml = self._parse_volume_ml(data.get("volume_text") or data.get("spec") or "")
        abv = self._parse_abv(data.get("abv_text") or data.get("spec") or "")
        description = data.get("description") or ""
        food_pairing = data.get("food_pairing") or ""
        image_url = urljoin(BASE_URL, PRODUCT_IMAGE_PATH.format(product_id=source_id))
        image_code_name = self._build_image_code_name(source_id, alcohol_type, volume_ml, abv)

        return TheSoolProduct(
            source_id=source_id,
            source_name="TheSool",
            source_url=f"{urljoin(BASE_URL, VIEW_PATH)}?productId={source_id}",
            name=name,
            brewery={
                "name": data.get("brewery_name") or "",
                "region": self._region_from_address(data.get("brewery_address") or ""),
                "address": data.get("brewery_address") or "",
                "phone": data.get("brewery_phone") or "",
                "homepage_url": data.get("brewery_homepage_url") or "",
            },
            drink={
                "name": name,
                "ingredients": data.get("ingredients") or "",
                "alcohol_type": alcohol_type,
                "alcohol_type_label": category,
                "abv": abv,
                "volume_ml": volume_ml,
                "food_pairing": food_pairing,
                "taste_profile": self._infer_taste_profile(description, food_pairing),
            },
            product={
                "description": description,
                "description_image_url": image_url,
                "price": None,
                "source_name": "TheSool",
                "source_url": f"{urljoin(BASE_URL, VIEW_PATH)}?productId={source_id}",
                "status": "INACTIVE",
            },
            image={
                "source_url": image_url,
                "code_name": image_code_name,
                "storage_key": f"products/thesool/{IMAGE_CATEGORY_CODE.get(alcohol_type, 'etc')}/{image_code_name}",
                "is_main": True,
            },
            raw={
                "category": category,
                "spec": data.get("spec") or "",
                "awards": data.get("awards") or "",
                "extra": data.get("extra") or "",
                "labels": data.get("labels") or [],
                "content_hash": self._hash(
                    "|".join(
                        [
                            source_id,
                            name,
                            data.get("ingredients") or "",
                            description,
                            food_pairing,
                        ]
                    )
                ),
            },
        )

    def _build_image_code_name(self, source_id: str, alcohol_type: str, volume_ml: int | None, abv: float | None) -> str:
        type_code = IMAGE_CATEGORY_CODE.get(alcohol_type, "etc")
        volume_code = f"vol{volume_ml}" if volume_ml else "volx"
        if abv is None:
            abv_code = "abvx"
        else:
            abv_code = f"abv{str(abv).replace('.', 'p').rstrip('0').rstrip('p')}"
        return f"thesool-{type_code}-{volume_code}-{abv_code}-{source_id.lower()}.webp"

    def _infer_taste_profile(self, description: str, food_pairing: str) -> dict[str, float]:
        text = f"{description} {food_pairing}"
        sweetness = self._score(text, ["달콤", "단맛", "달달", "꿀", "과일", "감귤", "복분자"], default=2.5)
        acidity = self._score(text, ["산미", "새콤", "상큼", "신맛", "감귤", "요구르트"], default=2.5)
        body = self._score(text, ["묵직", "진한", "걸쭉", "깊은", "농후", "풍부"], default=2.5)
        carbonation = self._score(text, ["탄산", "청량", "스파클링", "경쾌"], default=0.0)
        bitterness = self._score(text, ["쌉쌀", "쓴맛", "드라이", "담백"], default=2.0)
        aroma = self._score(text, ["향", "꽃향", "과실향", "풍미", "은은", "그윽"], default=2.5)
        return {
            "sweetness_level": sweetness,
            "acidity_level": acidity,
            "body_level": body,
            "carbonation_level": carbonation,
            "bitterness_level": bitterness,
            "aroma_level": aroma,
            "inference_note": "Keyword-based draft values. Review before production import.",
        }

    def _score(self, text: str, keywords: list[str], default: float) -> float:
        hits = sum(1 for keyword in keywords if keyword in text)
        return min(5.0, round(default + hits * 0.7, 1))

    def _map_alcohol_type(self, category: str, name: str) -> str:
        text = f"{category} {name}"
        for keyword, alcohol_type in ALCOHOL_TYPE_MAP.items():
            if keyword in text:
                return alcohol_type
        return "YAKJU"

    def _parse_volume_ml(self, value: str) -> int | None:
        match = re.search(r"(\d+(?:\.\d+)?)\s*ml", value, flags=re.IGNORECASE)
        return int(float(match.group(1))) if match else None

    def _parse_abv(self, value: str) -> float | None:
        match = re.search(r"(\d+(?:\.\d+)?)\s*%", value)
        return float(match.group(1)) if match else None

    def _region_from_address(self, address: str) -> str:
        for region in REGION_PREFIXES:
            if address.startswith(region):
                return region
        return ""

    def _info_value(self, block: str, label: str) -> str:
        pattern = rf'<div class="subject">\s*{re.escape(label)}\s*</div>\s*<div class="info[^"]*">([\s\S]*?)</div>'
        return self._clean(self._first_match(block, pattern))

    def _detail_value(self, page_html: str, label: str) -> str:
        pattern = rf"<li>\s*<strong>{re.escape(label)}</strong>\s*<span>([\s\S]*?)</span>\s*</li>"
        return self._clean(self._first_match(page_html, pattern))

    def _section_text(self, page_html: str, class_name: str) -> str:
        pattern = rf'<dd class="{class_name}">[\s\S]*?<div class="text">([\s\S]*?)</div>\s*</dd>'
        return self._clean(self._first_match(page_html, pattern))

    def _place_value(self, page_html: str, label: str) -> str:
        pattern = rf"<li><strong>{re.escape(label)}</strong>\s*<span>([\s\S]*?)</span></li>"
        return self._clean(self._first_match(page_html, pattern))

    def _place_homepage(self, page_html: str) -> str:
        pattern = r"<li><strong>홈페이지</strong>[\s\S]*?<a href=\"([^\"]+)\""
        return self._clean(self._first_match(page_html, pattern))

    def _place_phone(self, page_html: str) -> str:
        pattern = r"<li><strong>문의</strong>([\s\S]*?)</li>"
        return self._clean(self._first_match(page_html, pattern))

    def _first_match(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(1) if match else ""

    def _clean(self, value: str) -> str:
        value = re.sub(r"<script[\s\S]*?</script>", "", value)
        value = re.sub(r"<style[\s\S]*?</style>", "", value)
        value = re.sub(r"<[^>]+>", " ", value)
        value = html.unescape(value)
        value = value.replace("\xa0", " ")
        return re.sub(r"\s+", " ", value).strip()

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _resolve_output_path(self, output: str) -> Path:
        output_path = Path(output)
        if output_path.is_absolute():
            return output_path

        artifacts_dir = os.environ.get("ARTIFACTS_DIR")
        if artifacts_dir:
            parts = output_path.parts
            if parts and parts[0] == "artifacts":
                output_path = Path(*parts[1:])
            return Path(artifacts_dir) / output_path

        return Path.cwd() / output_path
