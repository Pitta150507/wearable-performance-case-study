#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import DATA_DIR, FIGURES_DIR, ensure_output_dirs, parse_iso_date


WIDTH = 1200
HEIGHT = 720
MARGIN = 95
INK = "#18202A"
MUTED = "#637083"
GRID = "#E4E8EE"
BLUE = "#2F6FED"
GOLD = "#D39E2F"
PINK = "#C84E74"
OLIVE = "#6E8B3D"


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def new_canvas(title: str, subtitle: str = ""):
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)
    draw.text((50, 32), title, fill=INK, font=font(34, True))
    if subtitle:
        draw.text((50, 78), subtitle, fill=MUTED, font=font(18))
    return img, draw


def scale(values, low_px, high_px, reverse=False):
    clean = [v for v in values if v is not None]
    if not clean:
        return lambda _: (low_px + high_px) / 2
    lo, hi = min(clean), max(clean)
    if lo == hi:
        lo -= 1
        hi += 1
    def mapper(value):
        if value is None:
            return None
        pct = (value - lo) / (hi - lo)
        if reverse:
            pct = 1 - pct
        return low_px + pct * (high_px - low_px)
    return mapper


def draw_axes(draw, x0, y0, x1, y1, y_values, y_label: str):
    draw.line((x0, y1, x1, y1), fill=INK, width=2)
    draw.line((x0, y0, x0, y1), fill=INK, width=2)
    clean = [v for v in y_values if v is not None]
    if clean:
        lo, hi = min(clean), max(clean)
        if lo == hi:
            lo -= 1
            hi += 1
        for i in range(5):
            value = lo + (hi - lo) * i / 4
            y = y1 - (y1 - y0) * i / 4
            draw.line((x0, y, x1, y), fill=GRID, width=1)
            draw.text((20, y - 10), f"{value:.1f}", fill=MUTED, font=font(14))
    draw.text((x0, y0 - 34), y_label, fill=MUTED, font=font(15))


def line_chart(points, title, subtitle, y_label, out_path):
    img, draw = new_canvas(title, subtitle)
    x0, y0, x1, y1 = MARGIN, 135, WIDTH - 55, HEIGHT - 90
    values = [p[1] for p in points]
    draw_axes(draw, x0, y0, x1, y1, values, y_label)
    if not points:
        draw.text((x0 + 20, y0 + 40), "No data available", fill=MUTED, font=font(22))
        img.save(out_path)
        return
    xs = scale(list(range(len(points))), x0, x1)
    ys = scale(values, y1, y0)
    coords = [(xs(i), ys(v)) for i, (_, v) in enumerate(points) if v is not None]
    if len(coords) > 1:
        draw.line(coords, fill=BLUE, width=4)
    for x, y in coords:
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=BLUE)
    for i in range(0, len(points), max(1, len(points) // 8)):
        x = xs(i)
        label = points[i][0]
        draw.text((x - 35, y1 + 16), label, fill=MUTED, font=font(13))
    img.save(out_path)


def bar_chart(labels, values, title, subtitle, y_label, out_path, color=BLUE):
    img, draw = new_canvas(title, subtitle)
    x0, y0, x1, y1 = MARGIN, 135, WIDTH - 55, HEIGHT - 110
    draw_axes(draw, x0, y0, x1, y1, values, y_label)
    if not values:
        draw.text((x0 + 20, y0 + 40), "No data available", fill=MUTED, font=font(22))
        img.save(out_path)
        return
    ys = scale(values + [0], y1, y0)
    bar_w = min(140, (x1 - x0) / max(1, len(values)) * 0.55)
    for i, (label, value) in enumerate(zip(labels, values, strict=False)):
        cx = x0 + (i + 0.5) * (x1 - x0) / len(values)
        y = ys(value)
        draw.rounded_rectangle((cx - bar_w / 2, y, cx + bar_w / 2, y1), radius=4, fill=color)
        draw.text((cx - 48, y1 + 15), label, fill=MUTED, font=font(14))
        draw.text((cx - 28, y - 26), f"{value:.1f}", fill=INK, font=font(15, True))
    img.save(out_path)


def scatter_panels(rows, out_path):
    metrics = [
        ("run_km_28d", "28d run km"),
        ("sleep_avg_hours_7d", "7d sleep h"),
        ("hrv_avg_28d", "28d HRV"),
        ("rhr_avg_28d", "28d HR proxy"),
        ("acute_load_nearest", "acute load"),
        ("vo2max_nearest", "VO2max"),
    ]
    img, draw = new_canvas(
        "Relative Performance Relationships",
        "Small-n exploratory scatter plots; lower relative performance is better.",
    )
    panel_w, panel_h = 340, 210
    start_x, start_y = 70, 140
    for idx, (metric, label) in enumerate(metrics):
        col, row = idx % 3, idx // 3
        x0 = start_x + col * 370
        y0 = start_y + row * 255
        x1 = x0 + panel_w
        y1 = y0 + panel_h
        draw.rectangle((x0, y0, x1, y1), outline=GRID, width=1)
        points = [(to_float(r.get(metric)), to_float(r.get("relative_performance_pct"))) for r in rows]
        points = [(x, y) for x, y in points if x is not None and y is not None]
        draw.text((x0, y0 - 28), label, fill=INK, font=font(17, True))
        if not points:
            draw.text((x0 + 20, y0 + 75), "Missing", fill=MUTED, font=font(18))
            continue
        xs = scale([p[0] for p in points], x0 + 35, x1 - 20)
        ys = scale([p[1] for p in points], y1 - 32, y0 + 20)
        for x_val, y_val in points:
            x = xs(x_val)
            y = ys(y_val)
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=PINK)
        draw.text((x0 + 12, y1 - 24), "x", fill=MUTED, font=font(12))
        draw.text((x0 + 12, y0 + 6), "rel %", fill=MUTED, font=font(12))
    img.save(out_path)


def main() -> None:
    ensure_output_dirs()
    daily = read_csv(DATA_DIR / "daily_training_summary.csv")
    races = read_csv(DATA_DIR / "race_context_dataset.csv")

    weekly = defaultdict(float)
    for row in daily:
        day = parse_iso_date(row["date"])
        iso = day.isocalendar()
        label = f"{iso.year}-W{iso.week:02d}"
        weekly[label] += float(row["run_km"] or 0)
    weekly_points = [(k, round(v, 1)) for k, v in sorted(weekly.items())]

    race_points = [
        (r["race_date"], to_float(r["relative_performance_pct"]))
        for r in sorted(races, key=lambda x: x["race_date"])
        if to_float(r["relative_performance_pct"]) is not None
    ]
    race_labels = [datetime.strptime(r["race_date"], "%Y-%m-%d").strftime("%d %b") for r in races]
    run28 = [to_float(r["run_km_28d"]) or 0 for r in races]

    line_chart(
        weekly_points,
        "Running Volume Timeline",
        "Weekly running distance from Garmin summarized activities, 2022-2026.",
        "km per week",
        FIGURES_DIR / "running_volume_timeline.png",
    )
    line_chart(
        race_points,
        "Race Relative Performance Timeline",
        "Official FIDAL results, normalized within each event. Lower percentage is closer to event best.",
        "% from event best",
        FIGURES_DIR / "race_performance_timeline.png",
    )
    bar_chart(
        race_labels,
        run28,
        "28-Day Running Volume Before Races",
        "Pre-race windows exclude the race day.",
        "km",
        FIGURES_DIR / "prerace_28d_running_volume.png",
        color=GOLD,
    )
    bar_chart(
        race_labels,
        [to_float(r["sleep_avg_hours_7d"]) or 0 for r in races],
        "7-Day Sleep Before Races",
        "Average sleep hours in the seven days before each race.",
        "hours",
        FIGURES_DIR / "sleep_before_races.png",
        color=OLIVE,
    )
    scatter_panels(races, FIGURES_DIR / "metric_relationships.png")
    print(f"Wrote PNG figures to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
