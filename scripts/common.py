from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VAULT_ROOT = PROJECT_ROOT.parents[1]
GARMIN_EXPORT_DIR = Path(
    os.environ.get(
        "GARMIN_EXPORT_DIR",
        "/Users/andreabertoldo/.gemini/antigravity/scratch/andrea-second-brain/raw/running/garmin/export-2026-06-04",
    )
)
DATA_DIR = PROJECT_ROOT / "data"
FIGURES_DIR = PROJECT_ROOT / "figures"

ATHLETE_ID = "single_athlete_001"
FIDAL_PROFILE_URL = "https://www.fidal.it/atleta/BERTOLDO+Andrea/eK2Rk5OmaWM%3D"

USER_VERIFIED_RACES = []


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_output_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def garmin_local_date(ms_value: Any) -> date | None:
    if ms_value in (None, ""):
        return None
    try:
        # Garmin local timestamps are epoch-like millisecond values shifted to the
        # local wall-clock time. Reading them in UTC preserves the local date.
        return datetime.fromtimestamp(float(ms_value) / 1000, tz=timezone.utc).date()
    except (TypeError, ValueError, OSError):
        return None


def date_from_any(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return garmin_local_date(value)
    text = str(value).strip()
    if not text:
        return None
    if text.isdigit():
        return garmin_local_date(int(text))
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text[:26], fmt).date()
        except ValueError:
            continue
    return None


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def round_float(value: Any, digits: int = 2) -> float | None:
    if value in (None, ""):
        return None
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def pre_race_window(race_day: date, days: int) -> tuple[date, date]:
    return race_day - timedelta(days=days), race_day - timedelta(days=1)


def fitness_dir() -> Path:
    return GARMIN_EXPORT_DIR / "DI_CONNECT" / "DI-Connect-Metrics"


def wellness_dir() -> Path:
    return GARMIN_EXPORT_DIR / "DI_CONNECT" / "DI-Connect-Wellness"


def fitness_export_dir() -> Path:
    return GARMIN_EXPORT_DIR / "DI_CONNECT" / "DI-Connect-Fitness"
