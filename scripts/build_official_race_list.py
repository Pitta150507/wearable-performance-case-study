#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import urllib.request
from html import unescape
from pathlib import Path

from common import ATHLETE_ID, DATA_DIR, FIDAL_PROFILE_URL, ensure_output_dirs


EXCLUDED_FROM_CONTEXT = {"Salto in lungo/LJ", "Vortex", "TETRATHLON"}


def strip_html(value: str) -> str:
    text = re.sub(r"<.*?>", "", value, flags=re.S)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def parse_time_seconds(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    if ":" not in text:
        try:
            return float(text)
        except ValueError:
            return None
    parts = text.split(":")
    try:
        if len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    except ValueError:
        return None
    return None


def distance_for_event(event: str, performance: str) -> int | None:
    normalized = event.lower()
    if "corsa 30" in normalized:
        try:
            return int(float(performance.replace(",", ".")))
        except ValueError:
            return None
    if "km 10" in normalized:
        return 10000
    if "km 5" in normalized:
        return 5000
    if "siepi" in normalized:
        match = re.search(r"(\d+)", normalized)
        return int(match.group(1)) if match else None
    match = re.search(r"(\d+)\s*(?:metri|piani|m\b)", normalized)
    if match:
        return int(match.group(1))
    if normalized.startswith("60 hs"):
        return 60
    return None


def official_time_for_event(event: str, performance: str) -> tuple[float | None, str]:
    if "corsa 30" in event.lower():
        return 1800.0, "30:00"
    seconds = parse_time_seconds(performance)
    return seconds, performance


def surface_type(raw_type: str) -> str:
    return {"P": "Pista", "I": "Indoor", "S": "Strada"}.get(raw_type, raw_type)


def timing_type(raw_crono: str) -> str:
    return {"E": "Elettrico", "M": "Manuale", "N": "Non specificato"}.get(raw_crono, raw_crono)


def analysis_scope(event: str, distance_m: int | None) -> str:
    lower = event.lower()
    if event in EXCLUDED_FROM_CONTEXT:
        return "field_or_multi_event"
    if distance_m is None:
        return "unknown"
    if "marcia" in lower:
        return "race_walk"
    if "siepi" in lower:
        return "endurance"
    if "strada" in lower or "corsa 30" in lower:
        return "endurance"
    if distance_m >= 800:
        return "endurance"
    return "sprint_middle"


def parse_profile_html(html: str) -> list[dict]:
    rows = []
    for section in re.finditer(r'<h2 class="title-table">(.*?)</h2>(.*?)(?=<h2 class="title-table">|<h2|Attenzione:)', html, re.S):
        event = strip_html(section.group(1))
        table_html = section.group(2)
        for row_html in re.findall(r"<tr>(.*?)</tr>", table_html, re.S):
            cells = [strip_html(cell) for cell in re.findall(r"<td[^>]*>(.*?)</td>", row_html, re.S)]
            if len(cells) < 9:
                continue
            year, day_month, raw_type, raw_crono, category, placement, performance, wind, city = cells[:9]
            if not year.isdigit() or "/" not in day_month:
                continue
            day, month = day_month.split("/")
            race_date = f"{year}-{int(month):02d}-{int(day):02d}"
            distance_m = distance_for_event(event, performance)
            official_seconds, official_time_text = official_time_for_event(event, performance)
            scope = analysis_scope(event, distance_m)
            include = "yes" if scope not in {"field_or_multi_event", "unknown"} and official_seconds is not None and distance_m else "no"
            notes = ""
            if "corsa 30" in event.lower():
                notes = f"FIDAL performance is distance covered in 30 minutes: {performance} m."
            if scope == "field_or_multi_event":
                notes = "Stored in FIDAL results inventory but excluded from race-context windows because it is not a timed running/race-walk performance."
            rows.append(
                {
                    "athlete_id": ATHLETE_ID,
                    "race_date": race_date,
                    "fidal_event": event,
                    "race_name": f"{event} - {city}",
                    "distance_m": distance_m or "",
                    "official_time_seconds": official_seconds if official_seconds is not None else "",
                    "official_time_text": official_time_text,
                    "official_performance_raw": performance,
                    "surface_type": surface_type(raw_type),
                    "timing_type": timing_type(raw_crono),
                    "category": category,
                    "placement": placement,
                    "wind": wind,
                    "city": city,
                    "source": "FIDAL athlete profile",
                    "source_url": FIDAL_PROFILE_URL,
                    "analysis_scope": scope,
                    "include_in_race_context": include,
                    "notes": notes,
                    "confidence_level": "high",
                }
            )
    return sorted(rows, key=lambda row: (row["race_date"], row["fidal_event"], row["official_performance_raw"]))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ensure_output_dirs()
    with urllib.request.urlopen(FIDAL_PROFILE_URL, timeout=20) as response:
        html = response.read().decode("utf-8", "replace")
    rows = parse_profile_html(html)
    fieldnames = [
        "athlete_id",
        "race_date",
        "fidal_event",
        "race_name",
        "distance_m",
        "official_time_seconds",
        "official_time_text",
        "official_performance_raw",
        "surface_type",
        "timing_type",
        "category",
        "placement",
        "wind",
        "city",
        "source",
        "source_url",
        "analysis_scope",
        "include_in_race_context",
        "notes",
        "confidence_level",
    ]
    out = DATA_DIR / "fidal_official_results.csv"
    write_csv(out, rows, fieldnames)
    included = sum(1 for row in rows if row["include_in_race_context"] == "yes")
    print(f"Wrote {out}")
    print(f"FIDAL result rows: {len(rows)}")
    print(f"Race-context eligible rows: {included}")


if __name__ == "__main__":
    main()
