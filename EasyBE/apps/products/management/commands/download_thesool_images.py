import argparse
import json
import os
import time
from io import BytesIO
from pathlib import Path
from typing import Any

import requests
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, UnidentifiedImageError


class Command(BaseCommand):
    help = "Download TheSool product images using the prepared Moeun import JSON."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--input",
            default="artifacts/data/thesool_import.json",
            help="Prepared Moeun import JSON path.",
        )
        parser.add_argument(
            "--output-dir",
            default="artifacts/data/images",
            help="Base image output directory.",
        )
        parser.add_argument("--delay", type=float, default=0.05)
        parser.add_argument("--limit", type=int, default=0, help="0 means no limit.")
        parser.add_argument("--force", action="store_true")
        parser.add_argument("--quality", type=int, default=90)

    def handle(self, *args: Any, **options: Any) -> None:
        input_path = self._resolve_path(options["input"])
        output_dir = self._resolve_path(options["output_dir"])

        if not input_path.exists():
            raise CommandError(f"input file does not exist: {input_path}")

        payload = json.loads(input_path.read_text(encoding="utf-8"))
        products = payload.get("products", [])
        if not isinstance(products, list):
            raise CommandError("input products must be a list")

        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "MoeunImageDownloader/1.0 (+https://thesool.com)",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            }
        )

        limit = options["limit"]
        if limit > 0:
            products = products[:limit]

        result = {
            "total": len(products),
            "downloaded": 0,
            "skipped_existing": 0,
            "failed": 0,
            "failures": [],
        }

        for index, product in enumerate(products, start=1):
            image = product["images"][0]
            source_url = image["image_url"]
            storage_key = image["storage_key"]
            target_path = output_dir / storage_key

            if target_path.exists() and not options["force"]:
                result["skipped_existing"] += 1
                continue

            try:
                self._download_webp(
                    session=session,
                    source_url=source_url,
                    target_path=target_path,
                    quality=options["quality"],
                )
            except (requests.RequestException, OSError, UnidentifiedImageError) as exc:
                result["failed"] += 1
                result["failures"].append(
                    {
                        "source_id": product["source"]["source_id"],
                        "name": product["drink"]["name"],
                        "source_url": source_url,
                        "error": str(exc),
                    }
                )
                continue

            result["downloaded"] += 1
            if result["downloaded"] % 100 == 0:
                self.stdout.write(f"{index}/{len(products)} images processed")
            time.sleep(options["delay"])

        manifest_path = output_dir / "thesool_image_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.stdout.write(
            self.style.SUCCESS(
                "images done: "
                f"downloaded={result['downloaded']}, "
                f"skipped={result['skipped_existing']}, "
                f"failed={result['failed']} -> {output_dir}"
            )
        )

    def _download_webp(
        self,
        *,
        session: requests.Session,
        source_url: str,
        target_path: Path,
        quality: int,
    ) -> None:
        response = session.get(source_url, timeout=20)
        response.raise_for_status()

        with Image.open(BytesIO(response.content)) as image:
            converted = image.convert("RGBA") if image.mode in ("P", "LA") else image.convert("RGB")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            converted.save(target_path, format="WEBP", quality=quality, method=6)

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
