#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

from common import DATA_DIR, GARMIN_EXPORT_DIR, ensure_output_dirs, read_json


SENSITIVE_KEY_RE = re.compile(r"(activityid|deviceid|userid|userprofile|uuid|latitude|longitude|profileid)", re.I)
EMAIL_RE = re.compile(r"[^/\\]+@[^/\\]+")
PATH_USER_ID_RE = re.compile(r"(?:(?<=_)|(?<=/))\d{8}(?=(?:_|\./|\.|/))")


def sanitize_path(path: Path) -> str:
    rel = str(path.relative_to(GARMIN_EXPORT_DIR))
    rel = EMAIL_RE.sub("<account>", rel)
    rel = PATH_USER_ID_RE.sub("<user_id>", rel)
    return rel


def safe_key_sample(sample: object, category: str) -> str:
    if category in {"private_account_or_social", "raw_or_binary_private"}:
        return ""
    if not isinstance(sample, dict):
        return ""
    keys = [key for key in sample.keys() if not SENSITIVE_KEY_RE.search(str(key))]
    return ", ".join(list(keys)[:18])


def summarize_json(path: Path, category: str) -> dict[str, str | int]:
    try:
        payload = read_json(path)
    except Exception as exc:  # noqa: BLE001 - inventory should keep going.
        return {
            "path": sanitize_path(path),
            "format": path.suffix.lower().lstrip("."),
            "top_level_type": "unreadable",
            "record_count": "",
            "key_sample": f"ERROR: {exc}",
        }

    record_count = ""
    sample = payload
    if isinstance(payload, list):
        record_count = len(payload)
        sample = payload[0] if payload else {}
    if isinstance(sample, dict) and len(sample) == 1:
        only_value = next(iter(sample.values()))
        if isinstance(only_value, list):
            record_count = len(only_value)
            sample = only_value[0] if only_value else {}

    return {
        "path": sanitize_path(path),
        "format": path.suffix.lower().lstrip("."),
        "top_level_type": type(payload).__name__,
        "record_count": record_count,
        "key_sample": safe_key_sample(sample, category),
    }


def classify(path: Path) -> str:
    name = path.name.lower()
    parent = str(path.parent).lower()
    if "summarizedactivities" in name:
        return "activities"
    if "personalrecord" in name:
        return "personal_records"
    if "sleepdata" in name:
        return "sleep"
    if "healthstatusdata" in name:
        return "hrv_rhr_health_status"
    if "maxmet" in name:
        return "vo2max"
    if "acutetrainingload" in name:
        return "acute_load"
    if "traininghistory" in name:
        return "training_status"
    if "runracepredictions" in name:
        return "race_predictions"
    if "uploaded-files" in parent or path.suffix.lower() == ".zip":
        return "raw_or_binary_private"
    if "user" in parent or "customer" in parent or "social" in parent:
        return "private_account_or_social"
    return "other"


def main() -> None:
    ensure_output_dirs()
    rows = []
    for path in sorted(GARMIN_EXPORT_DIR.rglob("*")):
        if not path.is_file():
            continue
        row = {
            "category": classify(path),
            "size_bytes": path.stat().st_size,
        }
        if path.suffix.lower() == ".json":
            row.update(summarize_json(path, row["category"]))
        else:
            row.update(
                {
                    "path": sanitize_path(path),
                    "format": path.suffix.lower().lstrip(".") or "none",
                    "top_level_type": "binary_or_other",
                    "record_count": "",
                    "key_sample": "",
                }
            )
        rows.append(row)

    out = DATA_DIR / "garmin_export_inventory.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "category",
                "path",
                "format",
                "top_level_type",
                "record_count",
                "size_bytes",
                "key_sample",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(row["category"] for row in rows)
    print(f"Wrote {out}")
    for category, count in counts.most_common():
        print(f"{category}: {count}")


if __name__ == "__main__":
    main()
