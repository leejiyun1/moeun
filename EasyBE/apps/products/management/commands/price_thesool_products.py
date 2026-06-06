import argparse
import html
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import Product


PRICE_RE = re.compile(r"(?<!\d)([1-9]\d{0,2}(?:,\d{3})+|[1-9]\d{3,6})\s*원")
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")

SOURCE_WEIGHTS = {
    "dailyshot.co": 35,
    "sooldamhwa.com": 35,
    "danawa.com": 30,
    "enuri.com": 30,
    "smartstore.naver.com": 25,
    "shopping.naver.com": 25,
    "11st.co.kr": 20,
    "gmarket.co.kr": 20,
    "auction.co.kr": 20,
    "lotteon.com": 20,
}
COMMERCE_DOMAINS = tuple(SOURCE_WEIGHTS.keys())

BAD_PRICE_WORDS = (
    "배송비",
    "배송",
    "무료배송",
    "적립",
    "포인트",
    "리뷰",
    "100ml",
    "10ml",
    "할인",
    "쿠폰",
)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class Command(BaseCommand):
    help = "Search web prices for imported TheSool products and optionally update local DB prices."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--output", default="artifacts/data/thesool_price_candidates.json")
        parser.add_argument("--start", type=int, default=0)
        parser.add_argument("--limit", type=int, default=0, help="0 means no limit.")
        parser.add_argument("--delay", type=float, default=1.0)
        parser.add_argument("--query-delay", type=float, default=0.2)
        parser.add_argument("--min-confidence", type=int, default=65)
        parser.add_argument("--commit", action="store_true")
        parser.add_argument("--force", action="store_true", help="Include products that already have prices.")
        parser.add_argument("--include-duckduckgo", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        output_path = self._resolve_path(options["output"])
        products = (
            Product.objects.select_related("drink", "drink__brewery")
            .filter(drink__isnull=False)
            .order_by("drink__name", "id")
        )
        if not options["force"]:
            products = products.filter(price=0)

        product_list = list(products)
        start = options["start"]
        if start > 0:
            product_list = product_list[start:]
        if options["limit"] > 0:
            product_list = product_list[: options["limit"]]

        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; MoeunPriceResearch/1.0)",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.6,en;q=0.5",
            }
        )

        records = []
        updates = []
        for index, product in enumerate(product_list, start=1):
            drink = product.drink
            queries = self._build_queries(product)
            record = {
                "product_id": str(product.id),
                "name": drink.name,
                "brewery": drink.brewery.name,
                "volume_ml": drink.volume_ml,
                "abv": str(drink.abv),
                "alcohol_type": drink.alcohol_type,
                "queries": queries,
                "selected_price": None,
                "confidence": 0,
                "source_url": "",
                "source_title": "",
                "candidates": [],
            }

            try:
                candidates = []
                for query in queries:
                    if options["include_duckduckgo"]:
                        try:
                            results = self._search(session, query)
                        except requests.RequestException:
                            results = []
                        candidates.extend(self._collect_candidates(session, product, results))
                    try:
                        candidates.extend(self._naver_candidates(session, product, query))
                    except requests.RequestException as exc:
                        record["last_search_error"] = str(exc)
                    time.sleep(options["query_delay"])
                    candidates = self._dedupe_candidates(
                        sorted(candidates, key=lambda item: (-item["confidence"], item["rank"], item["price"]))
                    )
                    if candidates and candidates[0]["confidence"] >= options["min_confidence"]:
                        break
            except requests.RequestException as exc:
                record["error"] = str(exc)
                candidates = []

            candidates = self._dedupe_candidates(
                sorted(candidates, key=lambda item: (-item["confidence"], item["rank"], item["price"]))
            )
            if candidates:
                best = candidates[0]
                record.update(
                    {
                        "selected_price": best["price"],
                        "confidence": best["confidence"],
                        "source_url": best["url"],
                        "source_title": best["title"],
                    }
                )
                record["candidates"] = candidates[:5]
                if best["confidence"] >= options["min_confidence"]:
                    updates.append((product.id, best["price"]))

            records.append(record)
            if index % 25 == 0:
                self.stdout.write(f"{index}/{len(product_list)} searched, update_candidates={len(updates)}")
            time.sleep(options["delay"])

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                {
                    "schema": "moeun.products.price_candidates.v1",
                    "searched": len(records),
                    "min_confidence": options["min_confidence"],
                    "commit": options["commit"],
                    "updates": len(updates),
                    "records": records,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        if options["commit"] and updates:
            self._apply_updates(updates)

        self.stdout.write(
            self.style.SUCCESS(
                f"price search done: searched={len(records)}, updates={len(updates)}, output={output_path}"
            )
        )

    def _build_queries(self, product: Product) -> list[str]:
        drink = product.drink
        brewery_name = drink.brewery.name
        queries = [
            f'"{drink.name}" 가격',
            f'"{drink.name}" {drink.volume_ml}ml 가격',
            f"{drink.name} 가격",
            f'site:dailyshot.co "{drink.name}"',
            f'site:sooldamhwa.com "{drink.name}"',
            f'site:danawa.com "{drink.name}"',
            f'site:enuri.com "{drink.name}"',
        ]
        if brewery_name and len(brewery_name) <= 24:
            queries.append(f'"{drink.name}" "{brewery_name}" 가격')
        return list(dict.fromkeys(queries))

    def _search(self, session: requests.Session, query: str) -> list[SearchResult]:
        response = session.get("https://duckduckgo.com/html/", params={"q": query}, timeout=20)
        response.raise_for_status()
        text = response.text
        chunks = re.split(r'<div class="result(?: results_links_deep)?', text)[1:16]
        results: list[SearchResult] = []
        for chunk in chunks:
            link_match = re.search(r'class="result__a" href="([^"]+)".*?>(.*?)</a>', chunk, re.S)
            if not link_match:
                continue
            raw_url = html.unescape(link_match.group(1))
            title = self._clean_html(link_match.group(2))
            snippet_match = re.search(r'class="result__snippet".*?>(.*?)</a>|class="result__snippet".*?>(.*?)</div>', chunk, re.S)
            snippet = self._clean_html((snippet_match.group(1) or snippet_match.group(2)) if snippet_match else "")
            url = self._decode_duckduckgo_url(raw_url)
            if url:
                results.append(SearchResult(title=title, url=url, snippet=snippet))
        return results

    def _collect_candidates(
        self,
        session: requests.Session,
        product: Product,
        results: list[SearchResult],
    ) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        for rank, result in enumerate(results[:8], start=1):
            result_text = f"{result.title} {result.snippet}"
            for price in self._extract_prices(result_text):
                candidates.append(
                    self._score_candidate(product, result, price, rank, "search_result", result_text)
                )

            if self._source_score(result.url) >= 20:
                try:
                    response = session.get(result.url, timeout=12)
                    if "text/html" not in response.headers.get("Content-Type", ""):
                        continue
                    page_text = self._clean_html(response.text[:300_000])
                    for price in self._extract_prices(page_text):
                        candidates.append(
                            self._score_candidate(
                                product,
                                result,
                                price,
                                rank,
                                "page",
                                f"{result_text} {page_text}",
                            )
                        )
                except requests.RequestException:
                    continue

        valid = [item for item in candidates if item["confidence"] >= 30]
        valid.sort(key=lambda item: (-item["confidence"], item["rank"], item["price"]))
        return self._dedupe_candidates(valid)

    def _naver_candidates(
        self,
        session: requests.Session,
        product: Product,
        query: str,
    ) -> list[dict[str, Any]]:
        response = session.get("https://search.naver.com/search.naver", params={"query": query}, timeout=20)
        response.raise_for_status()
        text = self._clean_html(response.text[:600_000])
        result = SearchResult(
            title=f"Naver search: {query}",
            url=response.url,
            snippet="",
        )
        candidates = []
        for price, context in self._extract_prices_with_context(text):
            if self._is_bundle_context(context):
                continue
            if self._has_other_volume(context, product.drink.volume_ml):
                continue
            candidate = self._score_naver_candidate(product, result, price, context)
            if candidate["confidence"] >= 30:
                candidates.append(candidate)
        candidates.sort(key=lambda item: (-item["confidence"], item["price"]))
        return self._dedupe_candidates(candidates)

    def _score_naver_candidate(
        self,
        product: Product,
        result: SearchResult,
        price: int,
        context: str,
    ) -> dict[str, Any]:
        drink = product.drink
        text = context.lower()
        confidence = 45
        name_tokens = self._tokens(drink.name)
        matched_name = sum(1 for token in name_tokens if token in text)
        if name_tokens:
            confidence += round((matched_name / len(name_tokens)) * 25)
        volume_matched = str(drink.volume_ml) in text or f"{drink.volume_ml:,}" in text
        if volume_matched:
            confidence += 18
        else:
            confidence = min(confidence, 58)
        if "최저" in context:
            confidence += 7
        if "상품가격" in context or "판매가격" in context or "구매하기" in context:
            confidence += 5
        if price < 1_000 or price > 300_000:
            confidence -= 30

        return {
            "price": price,
            "confidence": max(0, min(92, confidence)),
            "url": result.url,
            "title": result.title,
            "snippet": context[:300],
            "rank": 1,
            "match_type": "naver_search",
        }

    def _dedupe_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[int, str]] = set()
        unique = []
        for candidate in candidates:
            key = (candidate["price"], candidate["url"])
            if key in seen:
                continue
            seen.add(key)
            unique.append(candidate)
        return unique

    def _score_candidate(
        self,
        product: Product,
        result: SearchResult,
        price: int,
        rank: int,
        match_type: str,
        source_text: str,
    ) -> dict[str, Any]:
        drink = product.drink
        text = source_text.lower()
        title_text = f"{result.title} {result.snippet}".lower()
        confidence = max(0, 30 - (rank - 1) * 3)
        confidence += self._source_score(result.url)

        name_tokens = self._tokens(drink.name)
        brewery_tokens = self._tokens(drink.brewery.name)
        matched_name = sum(1 for token in name_tokens if token in text)
        if name_tokens:
            confidence += round((matched_name / len(name_tokens)) * 30)
        if brewery_tokens and any(token in text for token in brewery_tokens):
            confidence += 10
        volume_matched = str(drink.volume_ml) in text or f"{drink.volume_ml:,}" in text
        if volume_matched:
            confidence += 12
        if f"{int(drink.abv)}%" in text or str(drink.abv).rstrip("0").rstrip(".") + "%" in text:
            confidence += 5
        if match_type == "page":
            confidence += 5
        if not self._is_commerce_source(result.url):
            confidence = min(confidence, 55)
        if not volume_matched:
            confidence = min(confidence, 70)
        if "대용량" in title_text and drink.volume_ml < 1000:
            confidence = min(confidence, 50)
        if price < 1_000 or price > 300_000:
            confidence -= 30
        if any(word in text for word in BAD_PRICE_WORDS):
            confidence -= 8

        return {
            "price": price,
            "confidence": max(0, min(100, confidence)),
            "url": result.url,
            "title": result.title,
            "snippet": result.snippet[:300],
            "rank": rank,
            "match_type": match_type,
        }

    def _extract_prices(self, text: str) -> list[int]:
        prices = [price for price, _ in self._extract_prices_with_context(text)]
        return sorted(set(prices))

    def _extract_prices_with_context(self, text: str) -> list[tuple[int, str]]:
        prices = []
        for match in PRICE_RE.finditer(text):
            if match.end() < len(text) and text[match.end()] == "대":
                continue
            context = text[max(0, match.start() - 60) : match.end() + 60]
            if any(word in context for word in BAD_PRICE_WORDS):
                continue
            price = int(match.group(1).replace(",", ""))
            if 1_000 <= price <= 300_000:
                prices.append((price, context))
        return prices

    def _is_bundle_context(self, context: str) -> bool:
        lowered = context.lower()
        return any(
            word in lowered
            for word in (
                "2병",
                "3병",
                "4병",
                "5병",
                "6병",
                "10병",
                "1box",
                "box",
                "박스",
                "세트",
                "100ml당",
            )
        )

    def _has_other_volume(self, context: str, volume_ml: int) -> bool:
        volumes = {int(match) for match in re.findall(r"(\d{3,4})\s*ml", context.lower())}
        return any(volume != volume_ml for volume in volumes)

    def _source_score(self, url: str) -> int:
        host = urlparse(url).netloc.lower().replace("www.", "")
        for domain, score in SOURCE_WEIGHTS.items():
            if host == domain or host.endswith("." + domain):
                return score
        return 0

    def _is_commerce_source(self, url: str) -> bool:
        host = urlparse(url).netloc.lower().replace("www.", "")
        return any(host == domain or host.endswith("." + domain) for domain in COMMERCE_DOMAINS)

    def _tokens(self, value: str) -> list[str]:
        cleaned = re.sub(r"[\(\)\[\],·㈜주식회사농업회사법인]", " ", value.lower())
        return [token for token in SPACE_RE.split(cleaned) if len(token) >= 2]

    def _clean_html(self, value: str) -> str:
        value = html.unescape(value)
        value = TAG_RE.sub(" ", value)
        return SPACE_RE.sub(" ", value).strip()

    def _decode_duckduckgo_url(self, url: str) -> str:
        parsed = urlparse(url)
        if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
            uddg = parse_qs(parsed.query).get("uddg", [""])[0]
            return unquote(uddg)
        return url

    @transaction.atomic
    def _apply_updates(self, updates: list[tuple[Any, int]]) -> None:
        price_by_id = dict(updates)
        products = list(Product.objects.filter(id__in=price_by_id.keys()))
        for product in products:
            product.price = price_by_id[product.id]
            product.original_price = None
            product.discount = None
        Product.objects.bulk_update(products, ["price", "original_price", "discount"])

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
