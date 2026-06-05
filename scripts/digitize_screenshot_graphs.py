#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
from collections import defaultdict, deque
from datetime import date, timedelta
from pathlib import Path

from PIL import Image

from common import DATA_DIR, PROJECT_ROOT, ensure_output_dirs, parse_iso_date, round_float


SCREENSHOT_DIR = DATA_DIR / "manual_screenshots"
OCR_SWIFT = PROJECT_ROOT / "scripts" / "vision_ocr.swift"

MONTHS = {
    "gen": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "mag": 5,
    "giu": 6,
    "lug": 7,
    "ago": 8,
    "set": 9,
    "ott": 10,
    "nov": 11,
    "dic": 12,
}


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_ocr(paths: list[Path]) -> dict[str, list[dict]]:
    if not paths:
        return {}
    cmd = ["swift", str(OCR_SWIFT), *[str(path) for path in paths]]
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    observations: dict[str, list[dict]] = defaultdict(list)
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 7:
            continue
        image, conf, min_x, min_y, width, height, text = parts
        if conf == "ERROR":
            continue
        observations[image].append(
            {
                "confidence": float(conf),
                "min_x": float(min_x),
                "min_y": float(min_y),
                "width": float(width),
                "height": float(height),
                "text": text.strip(),
            }
        )
    return observations


def center(obs: dict) -> tuple[float, float]:
    return obs["min_x"] + obs["width"] / 2, obs["min_y"] + obs["height"] / 2


def parse_date_range(text: str, default_year: int = 2026) -> tuple[date, date] | None:
    cleaned = (
        text.lower()
        .replace("–", "-")
        .replace("—", "-")
        .replace(",", " ")
        .replace("  ", " ")
        .strip()
    )
    if "-" not in cleaned:
        return None
    pattern = re.compile(
        r"(?P<d1>\d{1,2})\s*(?P<m1>gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic)"
        r"(?:\s*(?P<y1>\d{4}))?\s*-\s*"
        r"(?P<d2>\d{1,2})\s*(?P<m2>gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic)"
        r"(?:\s*(?P<y2>\d{4}))?"
    )
    match = pattern.search(cleaned)
    if not match:
        same_month_pattern = re.compile(
            r"(?P<d1>\d{1,2})\s*(?P<m1>gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic)"
            r"(?:\s*(?P<y1>\d{4}))?\s*-\s*"
            r"(?P<d2>\d{1,2})(?:\s*(?P<y2>\d{4}))?"
        )
        same_month_match = same_month_pattern.search(cleaned)
        if same_month_match:
            y2 = int(same_month_match.group("y2") or same_month_match.group("y1") or default_year)
            y1 = int(same_month_match.group("y1") or y2)
            month = MONTHS[same_month_match.group("m1")]
            try:
                return (
                    date(y1, month, int(same_month_match.group("d1"))),
                    date(y2, month, int(same_month_match.group("d2"))),
                )
            except ValueError:
                return None
    if not match:
        return None
    y2 = int(match.group("y2") or match.group("y1") or default_year)
    y1 = int(match.group("y1") or y2)
    m1 = MONTHS[match.group("m1")]
    m2 = MONTHS[match.group("m2")]
    if not match.group("y1") and match.group("y2") and m1 > m2:
        y1 = y2 - 1
    if not match.group("y1") and not match.group("y2") and m1 > m2:
        y1 = default_year - 1
        y2 = default_year
    try:
        return date(y1, m1, int(match.group("d1"))), date(y2, m2, int(match.group("d2")))
    except ValueError:
        return None


def metadata_from_ocr(image_name: str, observations: list[dict]) -> dict:
    text_blob = " ".join(obs["text"] for obs in observations)
    metric_type = ""
    if "HRV Status" in text_blob:
        metric_type = "HRV"
    elif "Frequenza cardiaca" in text_blob:
        metric_type = "RHR"

    ranges = []
    for obs in observations:
        parsed = parse_date_range(obs["text"])
        if parsed:
            ranges.append((obs["min_y"], parsed, obs["text"]))
    ranges.sort(reverse=True, key=lambda item: item[0])
    start_date, end_date, range_text = ("", "", "")
    if ranges:
        start_date = ranges[0][1][0]
        end_date = ranges[0][1][1]
        range_text = ranges[0][2]

    y_labels = []
    for obs in observations:
        txt = obs["text"].strip()
        if not re.fullmatch(r"\d{2,3}", txt):
            continue
        cx, cy = center(obs)
        if cx > 0.14 or not (0.35 <= cy <= 0.65):
            continue
        y_labels.append({"value": int(txt), "cx": cx, "cy": cy, "text": txt})

    return {
        "source_image": image_name,
        "metric_type": metric_type,
        "start_date": start_date,
        "end_date": end_date,
        "range_text": range_text,
        "y_labels": y_labels,
    }


def fit_axis(y_labels: list[dict], height: int) -> tuple[float, float] | None:
    if len(y_labels) < 2:
        return None
    xs = []
    ys = []
    for label in y_labels:
        pixel_y = (1 - label["cy"]) * height
        xs.append(pixel_y)
        ys.append(label["value"])
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denom = sum((x - mean_x) ** 2 for x in xs)
    if denom == 0:
        return None
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denom
    intercept = mean_y - slope * mean_x
    return slope, intercept


def connected_components(mask: list[list[bool]]) -> list[dict]:
    height = len(mask)
    width = len(mask[0]) if height else 0
    seen = [[False] * width for _ in range(height)]
    comps = []
    for y in range(height):
        for x in range(width):
            if not mask[y][x] or seen[y][x]:
                continue
            q = deque([(x, y)])
            seen[y][x] = True
            pts = []
            while q:
                px, py = q.popleft()
                pts.append((px, py))
                for nx in (px - 1, px, px + 1):
                    for ny in (py - 1, py, py + 1):
                        if nx == px and ny == py:
                            continue
                        if 0 <= nx < width and 0 <= ny < height and mask[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            q.append((nx, ny))
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            comps.append(
                {
                    "area": len(pts),
                    "min_x": min(xs),
                    "max_x": max(xs),
                    "min_y": min(ys),
                    "max_y": max(ys),
                    "cx": sum(xs) / len(xs),
                    "cy": sum(ys) / len(ys),
                }
            )
    return comps


def hrv_mask(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    green = g > 115 and r < 55 and b < 120
    orange = r > 200 and 65 < g < 145 and b < 70
    red = r > 200 and g < 90 and b < 100
    return green or orange or red


def status_color(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    if g > 115 and r < 80:
        return "green"
    if r > 200 and 65 < g < 150:
        return "orange"
    if r > 200:
        return "red"
    return "unknown"


def digitize_hrv(path: Path, meta: dict) -> list[dict]:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    axis = fit_axis(meta["y_labels"], height)
    start = meta["start_date"]
    end = meta["end_date"]
    if not axis or not start or not end:
        return []

    sx = width / 946
    sy = height / 2048
    x0, x1 = round(123 * sx), round(864 * sx)
    y0, y1 = round(700 * sy), round(1305 * sy)
    crop = image.crop((x0, y0, x1, y1))
    mask = []
    for y in range(crop.height):
        row = []
        for x in range(crop.width):
            row.append(hrv_mask(crop.getpixel((x, y))))
        mask.append(row)
    comps = connected_components(mask)
    markers = []
    for comp in comps:
        box_w = comp["max_x"] - comp["min_x"] + 1
        box_h = comp["max_y"] - comp["min_y"] + 1
        if not (80 <= comp["area"] <= 1200 and 8 <= box_w <= 45 and 8 <= box_h <= 45):
            continue
        px = x0 + comp["cx"]
        py = y0 + comp["cy"]
        color = status_color(image.getpixel((int(round(px)), int(round(py)))))
        markers.append({"x": px, "y": py, "color": color})

    total_days = (end - start).days + 1
    if total_days <= 1:
        return []
    slope, intercept = axis
    by_day = {}
    for marker in markers:
        day_index = round((marker["x"] - x0) / ((x1 - x0) / (total_days - 1)))
        if not (0 <= day_index < total_days):
            continue
        value = slope * marker["y"] + intercept
        current = by_day.get(day_index)
        if current is None or abs(marker["x"] - (x0 + day_index * ((x1 - x0) / (total_days - 1)))) < current["x_error"]:
            by_day[day_index] = {
                "value": value,
                "status_color": marker["color"],
                "x_error": abs(marker["x"] - (x0 + day_index * ((x1 - x0) / (total_days - 1)))),
            }

    confidence = "high" if len(meta["y_labels"]) >= 3 and len(by_day) >= 20 else "medium" if len(by_day) >= 12 else "low"
    rows = []
    for day_index, item in sorted(by_day.items()):
        rows.append(
            {
                "source_image": path.name,
                "metric_type": "HRV",
                "date": (start + timedelta(days=day_index)).isoformat(),
                "estimated_value": round_float(item["value"], 1),
                "unit": "ms",
                "extraction_confidence": confidence,
                "y_axis_scale_available": "yes",
                "notes": f"Digitized from Garmin HRV Status 4-week graph; marker={item['status_color']}; approximate 7-day HRV status value, not raw nightly exact value.",
            }
        )
    return rows


def blue_mask(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return b > 115 and g > 55 and r < 95 and b > g + 25 and g > r + 20


def digitize_rhr(path: Path, meta: dict) -> list[dict]:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    axis = fit_axis(meta["y_labels"], height)
    start = meta["start_date"]
    end = meta["end_date"]
    if not axis or not start or not end:
        return []

    sx = width / 946
    sy = height / 2048
    x0, x1 = round(115 * sx), round(825 * sx)
    y0, y1 = round(735 * sy), round(1265 * sy)
    crop = image.crop((x0, y0, x1, y1))
    blue_pixels_by_x: dict[int, list[int]] = defaultdict(list)
    for y in range(crop.height):
        for x in range(crop.width):
            if blue_mask(crop.getpixel((x, y))):
                blue_pixels_by_x[x0 + x].append(y0 + y)

    weeks = max(2, round((end - start).days / 7) + 1)
    slope, intercept = axis
    rows = []
    found = 0
    values = []
    for i in range(weeks):
        px = round(x0 + i * (x1 - x0) / (weeks - 1))
        ys = []
        for nearby_x in range(px - 5, px + 6):
            ys.extend(blue_pixels_by_x.get(nearby_x, []))
        if not ys:
            values.append(None)
            continue
        ys.sort()
        py = ys[len(ys) // 2]
        value = slope * py + intercept
        values.append(value)
        found += 1

    confidence = "medium" if len(meta["y_labels"]) >= 3 and found >= 30 else "low"
    for i, value in enumerate(values):
        if value is None:
            continue
        rows.append(
            {
                "source_image": path.name,
                "metric_type": "RHR",
                "date": (start + timedelta(days=7 * i)).isoformat(),
                "estimated_value": round_float(value, 1),
                "unit": "bpm",
                "extraction_confidence": confidence,
                "y_axis_scale_available": "yes",
                "notes": "Digitized from Garmin annual heart-rate graph; blue series is weekly resting-heart-rate average, not a daily exact RHR value.",
            }
        )
    return rows


def combine_priority(export_rows: list[dict], digitized_rows: list[dict], metric: str) -> dict[date, dict]:
    combined = {}
    if metric == "HRV":
        export_col = "hrv_ms"
    else:
        export_col = "rhr_proxy_bpm"
    for row in export_rows:
        if row.get(export_col):
            combined[parse_iso_date(row["date"])] = {"source": "export", "value": float(row[export_col])}
    for row in digitized_rows:
        if row["metric_type"] != metric or row["extraction_confidence"] == "low":
            continue
        day = parse_iso_date(row["date"])
        if day not in combined:
            combined[day] = {"source": "screenshot_digitized", "value": float(row["estimated_value"])}
    return combined


def window_count(data_by_date: dict[date, dict], race_day: date, days: int) -> int:
    start = race_day - timedelta(days=days)
    end = race_day - timedelta(days=1)
    return sum(1 for day in data_by_date if start <= day <= end)


def make_coverage_audit(hrv_rows: list[dict], rhr_rows: list[dict]) -> list[dict]:
    races = read_csv(DATA_DIR / "race_context_dataset.csv")
    health = read_csv(DATA_DIR / "daily_health_summary.csv")

    export_hrv = {
        parse_iso_date(row["date"]): {"source": "export", "value": float(row["hrv_ms"])}
        for row in health
        if row.get("hrv_ms")
    }
    export_rhr = {
        parse_iso_date(row["date"]): {"source": "export", "value": float(row["rhr_proxy_bpm"])}
        for row in health
        if row.get("rhr_proxy_bpm")
    }
    shot_hrv = {
        parse_iso_date(row["date"]): {"source": "screenshot_digitized", "value": float(row["estimated_value"])}
        for row in hrv_rows
        if row["extraction_confidence"] in {"high", "medium"}
    }
    shot_rhr = {
        parse_iso_date(row["date"]): {"source": "screenshot_digitized", "value": float(row["estimated_value"])}
        for row in rhr_rows
        if row["extraction_confidence"] in {"high", "medium"}
    }
    combined_hrv = {**shot_hrv, **export_hrv}
    combined_rhr = {**shot_rhr, **export_rhr}

    out = []
    for race in races:
        race_day = parse_iso_date(race["race_date"])
        row = {"race_date": race["race_date"], "fidal_event": race["fidal_event"], "official_time_text": race["official_time_text"]}
        for days in (7, 14, 28, 56):
            row[f"hrv_export_days_{days}d"] = window_count(export_hrv, race_day, days)
            row[f"hrv_screenshot_days_{days}d"] = window_count(shot_hrv, race_day, days)
            row[f"hrv_combined_days_{days}d"] = window_count(combined_hrv, race_day, days)
            row[f"rhr_export_days_{days}d"] = window_count(export_rhr, race_day, days)
            row[f"rhr_screenshot_days_{days}d"] = window_count(shot_rhr, race_day, days)
            row[f"rhr_combined_days_{days}d"] = window_count(combined_rhr, race_day, days)
        out.append(row)
    return out


def compare_with_export(digitized_rows: list[dict], metric: str) -> dict:
    health = read_csv(DATA_DIR / "daily_health_summary.csv")
    export_col = "hrv_ms" if metric == "HRV" else "rhr_proxy_bpm"
    export = {parse_iso_date(row["date"]): float(row[export_col]) for row in health if row.get(export_col)}
    digitized = {
        parse_iso_date(row["date"]): float(row["estimated_value"])
        for row in digitized_rows
        if row["metric_type"] == metric and row["extraction_confidence"] in {"high", "medium"}
    }
    overlap = sorted(set(export) & set(digitized))
    mismatches = []
    tolerance = 3.0 if metric == "HRV" else 4.0
    for day in overlap:
        diff = digitized[day] - export[day]
        if abs(diff) > tolerance:
            mismatches.append((day, export[day], digitized[day], diff))
    recovered = sorted(set(digitized) - set(export))
    return {
        "export_days": len(export),
        "screenshot_days": len(digitized),
        "overlap_days": len(overlap),
        "mismatch_days": len(mismatches),
        "recovered_days": len(recovered),
        "mismatches": mismatches,
    }


def main() -> None:
    ensure_output_dirs()
    paths = sorted(SCREENSHOT_DIR.glob("IMG_*.PNG"))
    observations = run_ocr(paths)

    metadata_rows = []
    hrv_rows = []
    rhr_rows = []
    for path in paths:
        meta = metadata_from_ocr(path.name, observations.get(path.name, []))
        metadata_rows.append(
            {
                "source_image": path.name,
                "metric_type": meta["metric_type"] or "unknown",
                "start_date": meta["start_date"].isoformat() if isinstance(meta["start_date"], date) else "",
                "end_date": meta["end_date"].isoformat() if isinstance(meta["end_date"], date) else "",
                "visible_date_range_text": meta["range_text"],
                "y_axis_values": " ".join(str(label["value"]) for label in sorted(meta["y_labels"], key=lambda item: item["cy"], reverse=True)),
                "notes": "OCR metadata for screenshot graph digitization.",
            }
        )
        if meta["metric_type"] == "HRV":
            hrv_rows.extend(digitize_hrv(path, meta))
        elif meta["metric_type"] == "RHR":
            rhr_rows.extend(digitize_rhr(path, meta))

    digitized_fieldnames = [
        "source_image",
        "metric_type",
        "date",
        "estimated_value",
        "unit",
        "extraction_confidence",
        "y_axis_scale_available",
        "notes",
    ]
    write_csv(DATA_DIR / "hrv_graph_digitized.csv", hrv_rows, digitized_fieldnames)
    write_csv(DATA_DIR / "rhr_graph_digitized.csv", rhr_rows, digitized_fieldnames)

    manual_rows = []
    for row in hrv_rows + rhr_rows:
        metadata = next((m for m in metadata_rows if m["source_image"] == row["source_image"]), {})
        manual_rows.append(
            {
                "source_image": row["source_image"],
                "metric_type": row["metric_type"],
                "start_date": metadata.get("start_date", ""),
                "end_date": metadata.get("end_date", ""),
                "date": row["date"],
                "value": row["estimated_value"],
                "unit": row["unit"],
                "extraction_confidence": row["extraction_confidence"],
                "notes": row["notes"],
            }
        )
    write_csv(
        DATA_DIR / "manual_hrv_rhr_from_screenshots.csv",
        manual_rows,
        ["source_image", "metric_type", "start_date", "end_date", "date", "value", "unit", "extraction_confidence", "notes"],
    )
    write_csv(
        DATA_DIR / "manual_screenshot_inventory.csv",
        metadata_rows,
        ["source_image", "metric_type", "start_date", "end_date", "visible_date_range_text", "y_axis_values", "notes"],
    )

    coverage_rows = make_coverage_audit(hrv_rows, rhr_rows)
    coverage_fields = ["race_date", "fidal_event", "official_time_text"]
    for days in (7, 14, 28, 56):
        coverage_fields.extend(
            [
                f"hrv_export_days_{days}d",
                f"hrv_screenshot_days_{days}d",
                f"hrv_combined_days_{days}d",
                f"rhr_export_days_{days}d",
                f"rhr_screenshot_days_{days}d",
                f"rhr_combined_days_{days}d",
            ]
        )
    write_csv(DATA_DIR / "hrv_rhr_combined_coverage_audit.csv", coverage_rows, coverage_fields)

    hrv_compare = compare_with_export(hrv_rows, "HRV")
    rhr_compare = compare_with_export(rhr_rows, "RHR")
    report = build_report(metadata_rows, hrv_rows, rhr_rows, coverage_rows, hrv_compare, rhr_compare)
    (PROJECT_ROOT / "docs" / "HRV_RHR_Screenshot_Integration_Report.md").write_text(report, encoding="utf-8")

    print(f"Screenshot inventory rows: {len(metadata_rows)}")
    print(f"HRV digitized rows: {len(hrv_rows)}")
    print(f"RHR digitized rows: {len(rhr_rows)}")
    print(f"HRV export days: {hrv_compare['export_days']}; screenshot days: {hrv_compare['screenshot_days']}; recovered: {hrv_compare['recovered_days']}; mismatches: {hrv_compare['mismatch_days']}")
    print(f"RHR export days: {rhr_compare['export_days']}; screenshot days: {rhr_compare['screenshot_days']}; recovered: {rhr_compare['recovered_days']}; mismatches: {rhr_compare['mismatch_days']}")


def build_report(metadata_rows, hrv_rows, rhr_rows, coverage_rows, hrv_compare, rhr_compare) -> str:
    hrv_images = sorted({row["source_image"] for row in hrv_rows})
    rhr_images = sorted({row["source_image"] for row in rhr_rows})
    all_images = sorted({row["source_image"] for row in metadata_rows})
    digitized_images = sorted(set(hrv_images) | set(rhr_images))
    not_digitized_images = sorted(set(all_images) - set(digitized_images))

    def improved(metric: str, days: int) -> int:
        prefix = "hrv" if metric == "HRV" else "rhr"
        return sum(
            1
            for row in coverage_rows
            if int(row[f"{prefix}_export_days_{days}d"]) == 0 and int(row[f"{prefix}_combined_days_{days}d"]) > 0
        )

    report = f"""# HRV/RHR Screenshot Integration Report

## Summary

The screenshots were integrated as secondary/manual evidence. The Garmin export remains the primary source for exact HRV/RHR-proxy values. Screenshot-derived values are graph-digitized estimates and are not treated as equal-quality replacements for export JSON.

| Metric | Garmin export exact days | Screenshot digitized date-points | Overlap date-points | Mismatch date-points | Missing date-points recovered from screenshots |
|---|---:|---:|---:|---:|---:|
| HRV | {hrv_compare['export_days']} | {hrv_compare['screenshot_days']} | {hrv_compare['overlap_days']} | {hrv_compare['mismatch_days']} | {hrv_compare['recovered_days']} |
| RHR proxy/resting HR | {rhr_compare['export_days']} | {rhr_compare['screenshot_days']} | {rhr_compare['overlap_days']} | {rhr_compare['mismatch_days']} | {rhr_compare['recovered_days']} |

Important interpretation:

- HRV screenshots mostly show Garmin `HRV Status` 4-week graphs. The extracted values are approximate graph points, likely representing Garmin 7-day HRV status values rather than raw nightly HRV.
- RHR screenshots show annual heart-rate graphs. The blue series is digitized as approximate weekly resting-heart-rate averages, not daily exact RHR.
- Because the screenshot values are approximate and graph-derived, they were not merged into `race_context_dataset.csv` or the main statistical findings.
- Some screenshot ranges had no explicit year in the visible title. Those were assigned using the surrounding Garmin sequence and the current visible year context; this is adequate for coverage auditing but remains manual/secondary evidence.

## Images Used

- HRV screenshots with digitized graph points: {len(hrv_images)}
- RHR screenshots with digitized graph points: {len(rhr_images)}
- Images not digitized or not usable for graph extraction: {len(not_digitized_images)}
{("- Not digitized: " + ", ".join(not_digitized_images)) if not_digitized_images else ""}

## Extraction Method

For each screenshot, the workflow used visible OCR metadata to identify:

- metric type;
- visible date range;
- visible y-axis labels;
- plotted colored HRV markers or blue resting-HR graph line.

The graph was then digitized using pixel position and visible y-axis labels. Values are rounded to one decimal place only to avoid fake integer certainty.

Extraction confidence:

- `high`: readable date range, readable y-axis scale, and most plotted HRV markers detected.
- `medium`: readable date range and trend, but exact point placement or weekly spacing remains approximate.
- `low`: unclear/cropped/loading image or insufficient detected graph geometry.

## Coverage Improvement

Race-window counts below indicate how many of the 29 official FIDAL races had zero export coverage but gained at least one medium/high screenshot-derived point in the pre-race window.

| Window | HRV races improved | RHR races improved |
|---|---:|---:|
| 7 days | {improved('HRV', 7)} | {improved('RHR', 7)} |
| 14 days | {improved('HRV', 14)} | {improved('RHR', 14)} |
| 28 days | {improved('HRV', 28)} | {improved('RHR', 28)} |
| 56 days | {improved('HRV', 56)} | {improved('RHR', 56)} |

## Per-Race Combined Coverage

| Date | Event | HRV export 28d | HRV screenshot 28d | HRV combined 28d | RHR export 28d | RHR screenshot 28d | RHR combined 28d |
|---|---|---:|---:|---:|---:|---:|---:|
"""
    for row in coverage_rows:
        report += (
            f"| {row['race_date']} | {row['fidal_event']} | {row['hrv_export_days_28d']} | "
            f"{row['hrv_screenshot_days_28d']} | {row['hrv_combined_days_28d']} | "
            f"{row['rhr_export_days_28d']} | {row['rhr_screenshot_days_28d']} | {row['rhr_combined_days_28d']} |\n"
        )

    report += """
## Mismatch Check

Overlap mismatches are defined conservatively as screenshot estimate minus export value exceeding 3 ms for HRV or 4 bpm for RHR. These thresholds are not validation thresholds for scientific precision; they are a practical screen for obvious digitization disagreement.

"""
    if hrv_compare["mismatches"]:
        report += "HRV mismatch examples:\n\n"
        for day, export_value, screenshot_value, diff in hrv_compare["mismatches"][:15]:
            report += f"- {day.isoformat()}: export {export_value:.1f} ms, screenshot {screenshot_value:.1f} ms, diff {diff:.1f}.\n"
    else:
        report += "No HRV overlap mismatches exceeded the practical threshold.\n"

    report += "\n"
    if rhr_compare["mismatches"]:
        report += "RHR mismatch examples:\n\n"
        for day, export_value, screenshot_value, diff in rhr_compare["mismatches"][:15]:
            report += f"- {day.isoformat()}: export {export_value:.1f} bpm, screenshot {screenshot_value:.1f} bpm, diff {diff:.1f}.\n"
    else:
        report += "No RHR overlap mismatches exceeded the practical threshold.\n"

    report += """
## Statistical Decision

Screenshot data improves apparent HRV/RHR coverage, especially for older race windows, but it is not suitable for the main statistical analysis as currently extracted.

Reasons:

- The values are approximate graph digitizations, not exact Garmin export records.
- HRV screenshots show rolling/status-style values rather than clearly independent nightly raw HRV values.
- RHR screenshots are annual weekly averages, not daily values.
- The statistical dataset is already small, and adding approximate values would create a false sense of precision.

Therefore:

- `race_context_dataset.csv` was not rebuilt with screenshot-derived HRV/RHR.
- `stat_correlation_results.csv`, `stat_signal_ranking.csv`, and `docs/Statistical_Findings.md` were not rebuilt from screenshot-derived values.
- The earlier conclusion remains: export-derived HRV/RHR are too sparse for inference; screenshot evidence suggests historical Garmin app coverage exists, but not at sufficient extractable precision for main statistical claims.

## Outputs

- `data/manual_screenshots/`
- `data/manual_screenshot_inventory.csv`
- `data/manual_hrv_rhr_from_screenshots.csv`
- `data/hrv_graph_digitized.csv`
- `data/rhr_graph_digitized.csv`
- `data/hrv_rhr_combined_coverage_audit.csv`
"""
    return report


if __name__ == "__main__":
    main()
