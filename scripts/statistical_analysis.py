#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from common import DATA_DIR, FIGURES_DIR, PROJECT_ROOT, ensure_output_dirs


VARIABLES = [
    ("run_km_7d", "Run km 7d"),
    ("run_km_14d", "Run km 14d"),
    ("run_km_28d", "Run km 28d"),
    ("run_km_56d", "Run km 56d"),
    ("sleep_avg_hours_7d", "Sleep avg 7d"),
    ("sleep_avg_hours_14d", "Sleep avg 14d"),
    ("sleep_avg_hours_28d", "Sleep avg 28d"),
    ("hrv_avg_7d", "HRV avg 7d"),
    ("hrv_avg_14d", "HRV avg 14d"),
    ("hrv_avg_28d", "HRV avg 28d"),
    ("rhr_avg_7d", "RHR proxy 7d"),
    ("rhr_avg_14d", "RHR proxy 14d"),
    ("rhr_avg_28d", "RHR proxy 28d"),
    ("vo2max_nearest", "VO2max nearest"),
    ("acute_load_nearest", "Acute load nearest"),
]

GROUP_VARIABLES = [
    ("run_km_7d", "Run km 7d"),
    ("run_km_14d", "Run km 14d"),
    ("run_km_28d", "Run km 28d"),
    ("run_km_56d", "Run km 56d"),
    ("sleep_avg_hours_7d", "Sleep avg 7d"),
    ("sleep_avg_hours_14d", "Sleep avg 14d"),
    ("sleep_avg_hours_28d", "Sleep avg 28d"),
    ("hrv_avg_7d", "HRV avg 7d"),
    ("hrv_avg_14d", "HRV avg 14d"),
    ("hrv_avg_28d", "HRV avg 28d"),
    ("rhr_avg_7d", "RHR proxy 7d"),
    ("rhr_avg_14d", "RHR proxy 14d"),
    ("rhr_avg_28d", "RHR proxy 28d"),
    ("vo2max_nearest", "VO2max nearest"),
    ("acute_load_nearest", "Acute load nearest"),
]

OUTCOME = "performance_score"
WIDTH = 1500
HEIGHT = 900
INK = "#17202B"
MUTED = "#647084"
GRID = "#E4E8EE"
BLUE = "#2F6FED"
GOLD = "#D39E2F"
PINK = "#C84E74"
OLIVE = "#6E8B3D"
GREEN = "#427A5B"
RED = "#B95750"


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


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def rank_average(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    sorted_values = values[order]
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and sorted_values[j] == sorted_values[i]:
            j += 1
        avg_rank = (i + 1 + j) / 2
        ranks[order[i:j]] = avg_rank
        i = j
    return ranks


def pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return float("nan")
    x_centered = x - x.mean()
    y_centered = y - y.mean()
    denom = math.sqrt(float((x_centered**2).sum() * (y_centered**2).sum()))
    if denom == 0:
        return float("nan")
    return float((x_centered * y_centered).sum() / denom)


def beta_continued_fraction(a: float, b: float, x: float) -> float:
    max_iter = 200
    eps = 3e-12
    fpmin = 1e-300
    qab = a + b
    qap = a + 1
    qam = a - 1
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def regularized_incomplete_beta(a: float, b: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    log_bt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    bt = math.exp(log_bt)
    if x < (a + 1) / (a + b + 2):
        return bt * beta_continued_fraction(a, b, x) / a
    return 1 - bt * beta_continued_fraction(b, a, 1 - x) / b


def t_two_sided_p_from_r(r: float, n: int) -> float:
    if n < 3 or math.isnan(r):
        return float("nan")
    r = max(min(r, 0.999999999), -0.999999999)
    df = n - 2
    t = abs(r) * math.sqrt(df / (1 - r * r))
    x = df / (df + t * t)
    return float(regularized_incomplete_beta(df / 2, 0.5, x))


def fisher_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n < 4 or math.isnan(r) or abs(r) >= 1:
        return (float("nan"), float("nan"))
    z = math.atanh(r)
    se = 1 / math.sqrt(n - 3)
    zcrit = NormalDist().inv_cdf(1 - alpha / 2)
    return (math.tanh(z - zcrit * se), math.tanh(z + zcrit * se))


def correlation_table(df: pd.DataFrame) -> list[dict]:
    rows = []
    for column, label in VARIABLES:
        subset = df[[column, OUTCOME]].dropna()
        x = subset[column].to_numpy(dtype=float)
        y = subset[OUTCOME].to_numpy(dtype=float)
        n = len(subset)
        r = pearson_r(x, y) if n >= 3 else float("nan")
        p = t_two_sided_p_from_r(r, n)
        lo, hi = fisher_ci(r, n)
        sx = rank_average(x) if n >= 3 else np.array([])
        sy = rank_average(y) if n >= 3 else np.array([])
        rho = pearson_r(sx, sy) if n >= 3 else float("nan")
        sp = t_two_sided_p_from_r(rho, n)
        slo, shi = fisher_ci(rho, n)
        rows.append(
            {
                "variable": column,
                "label": label,
                "n": n,
                "pearson_r": round_or_blank(r, 4),
                "pearson_p": round_or_blank(p, 4),
                "pearson_ci_low": round_or_blank(lo, 4),
                "pearson_ci_high": round_or_blank(hi, 4),
                "spearman_rho": round_or_blank(rho, 4),
                "spearman_p": round_or_blank(sp, 4),
                "spearman_ci_low": round_or_blank(slo, 4),
                "spearman_ci_high": round_or_blank(shi, 4),
                "abs_pearson": round_or_blank(abs(r), 4) if not math.isnan(r) else "",
                "direction_for_better_performance": direction_text(r),
                "evidence_note": evidence_note(n, p, r),
            }
        )
    return sorted(rows, key=lambda row: float(row["abs_pearson"] or -1), reverse=True)


def evidence_note(n: int, p: float, r: float) -> str:
    if n < 5:
        return "Very sparse; treat as descriptive only."
    if math.isnan(r):
        return "No estimable relationship."
    if p < 0.05:
        return "Statistically notable in this dataset; not causal."
    if abs(r) >= 0.3:
        return "Moderate descriptive signal; p-value not below 0.05."
    return "Little linear signal in this dataset."


def direction_text(r: float) -> str:
    if math.isnan(r):
        return ""
    if r > 0:
        return "Higher variable associated with better event-relative performance."
    if r < 0:
        return "Higher variable associated with worse event-relative performance."
    return "No direction."


def round_or_blank(value: float, digits: int = 4):
    if value is None or math.isnan(value) or math.isinf(value):
        return ""
    return round(float(value), digits)


def quartile_comparison(df: pd.DataFrame) -> list[dict]:
    sorted_df = df.sort_values("relative_performance_pct", ascending=True)
    group_n = max(1, math.floor(len(sorted_df) * 0.25))
    best = sorted_df.head(group_n).copy()
    worst = sorted_df.tail(group_n).copy()
    rows = []
    for column, label in GROUP_VARIABLES:
        best_values = best[column].dropna().astype(float)
        worst_values = worst[column].dropna().astype(float)
        best_mean = float(best_values.mean()) if len(best_values) else float("nan")
        worst_mean = float(worst_values.mean()) if len(worst_values) else float("nan")
        diff = best_mean - worst_mean if not math.isnan(best_mean) and not math.isnan(worst_mean) else float("nan")
        pooled_sd = pooled_standard_deviation(best_values.to_numpy(dtype=float), worst_values.to_numpy(dtype=float))
        smd = diff / pooled_sd if pooled_sd and not math.isnan(diff) else float("nan")
        rows.append(
            {
                "variable": column,
                "label": label,
                "best_n": len(best_values),
                "worst_n": len(worst_values),
                "best_mean": round_or_blank(best_mean, 3),
                "worst_mean": round_or_blank(worst_mean, 3),
                "best_minus_worst": round_or_blank(diff, 3),
                "standardized_mean_difference": round_or_blank(smd, 4),
                "direction": group_direction(column, diff),
            }
        )
    return rows


def pooled_standard_deviation(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    numerator = (len(a) - 1) * float(np.var(a, ddof=1)) + (len(b) - 1) * float(np.var(b, ddof=1))
    denominator = len(a) + len(b) - 2
    if denominator <= 0:
        return float("nan")
    return math.sqrt(numerator / denominator)


def group_direction(column: str, diff: float) -> str:
    if math.isnan(diff):
        return "Not enough data."
    if abs(diff) < 1e-9:
        return "No mean difference."
    if column.startswith("rhr"):
        return "Best group lower RHR proxy." if diff < 0 else "Best group higher RHR proxy."
    return "Best group higher." if diff > 0 else "Best group lower."


def build_rankings(corr_rows: list[dict], quartile_rows: list[dict]) -> list[dict]:
    quartile_by_var = {row["variable"]: row for row in quartile_rows}
    ranking_rows = []
    max_n = max(int(row["n"]) for row in corr_rows) if corr_rows else 1
    for row in corr_rows:
        variable = row["variable"]
        q = quartile_by_var.get(variable, {})
        pearson = to_float(row["pearson_r"])
        spearman = to_float(row["spearman_rho"])
        n = int(row["n"])
        raw_score = np.nanmean([abs(pearson) if pearson is not None else np.nan, abs(spearman) if spearman is not None else np.nan])
        coverage_weight = min(1.0, n / max_n)
        score = raw_score * coverage_weight
        if n < 5:
            confidence = "very low"
        elif to_float(row["pearson_p"]) is not None and to_float(row["pearson_p"]) < 0.05:
            confidence = "moderate"
        elif score >= 0.3:
            confidence = "low"
        else:
            confidence = "low"
        ranking_rows.append(
            {
                "rank": "",
                "variable": variable,
                "label": row["label"],
                "signal_strength_score": round_or_blank(float(score), 4),
                "raw_correlation_strength": round_or_blank(float(raw_score), 4),
                "coverage_weight": round_or_blank(float(coverage_weight), 4),
                "pearson_r": row["pearson_r"],
                "spearman_rho": row["spearman_rho"],
                "n": n,
                "quartile_best_minus_worst": q.get("best_minus_worst", ""),
                "interpretation": interpret_signal(row, q),
                "confidence": confidence,
            }
        )
    ranking_rows = sorted(ranking_rows, key=lambda row: float(row["signal_strength_score"] or -1), reverse=True)
    for rank, row in enumerate(ranking_rows, 1):
        row["rank"] = rank
    return ranking_rows


def to_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def interpret_signal(corr_row: dict, qrow: dict) -> str:
    r = to_float(corr_row["pearson_r"])
    if r is None:
        return "Not enough complete observations."
    direction = "higher values align with better event-relative performance" if r > 0 else "higher values align with worse event-relative performance"
    return f"{direction}; {qrow.get('direction', 'quartile comparison unavailable')}"


def new_canvas(title: str, subtitle: str = ""):
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)
    draw.text((55, 35), title, fill=INK, font=font(38, True))
    if subtitle:
        draw.text((55, 86), subtitle, fill=MUTED, font=font(20))
    return img, draw


def draw_correlation_bar(corr_rows: list[dict], out_path: Path) -> None:
    rows = [row for row in corr_rows if row["pearson_r"] != ""]
    rows = sorted(rows, key=lambda row: float(row["pearson_r"]))
    img, draw = new_canvas(
        "Associations With Event-Relative Performance",
        "Pearson r vs performance_score = -relative_performance_pct; positive means higher variable aligns with better performance.",
    )
    x0, y0, x1, y1 = 420, 150, WIDTH - 120, HEIGHT - 75
    zero_x = x0 + (x1 - x0) / 2
    draw.line((zero_x, y0, zero_x, y1), fill=INK, width=2)
    for tick in [-1, -0.5, 0, 0.5, 1]:
        x = x0 + (tick + 1) / 2 * (x1 - x0)
        draw.line((x, y0, x, y1), fill=GRID if tick != 0 else INK, width=1)
        draw.text((x - 18, y1 + 14), f"{tick:g}", fill=MUTED, font=font(15))
    row_h = (y1 - y0) / len(rows)
    for i, row in enumerate(rows):
        y = y0 + i * row_h + row_h * 0.18
        label = row["label"]
        r = float(row["pearson_r"])
        p = row["pearson_p"]
        n = row["n"]
        bar_x = x0 + (r + 1) / 2 * (x1 - x0)
        color = GREEN if r > 0 else RED
        draw.text((55, y - 2), f"{label} (n={n}, p={p})", fill=INK, font=font(18))
        draw.rounded_rectangle((min(zero_x, bar_x), y, max(zero_x, bar_x), y + row_h * 0.55), radius=4, fill=color)
        draw.text((bar_x + (8 if r >= 0 else -58), y - 1), f"{r:+.2f}", fill=INK, font=font(16, True))
    img.save(out_path)


def draw_quartile_differences(quartile_rows: list[dict], out_path: Path) -> None:
    display = [row for row in quartile_rows if row["standardized_mean_difference"] != ""]
    display = sorted(display, key=lambda row: abs(float(row["standardized_mean_difference"])), reverse=True)
    img, draw = new_canvas(
        "Best vs Worst Quartile: Standardized Differences",
        "Bars show standardized mean difference; labels show raw best-minus-worst differences in each variable's own unit.",
    )
    x0, y0, x1, y1 = 460, 145, WIDTH - 285, HEIGHT - 85
    max_abs = max(abs(float(row["standardized_mean_difference"])) for row in display) or 1
    zero_x = x0 + (x1 - x0) / 2
    draw.line((zero_x, y0, zero_x, y1), fill=INK, width=2)
    row_h = (y1 - y0) / len(display)
    for i, row in enumerate(display):
        y = y0 + i * row_h + row_h * 0.18
        diff = float(row["best_minus_worst"])
        smd = float(row["standardized_mean_difference"])
        bar_x = zero_x + smd / max_abs * ((x1 - x0) / 2)
        color = BLUE if smd > 0 else GOLD
        draw.text((55, y - 2), row["label"], fill=INK, font=font(18))
        draw.rounded_rectangle((min(zero_x, bar_x), y, max(zero_x, bar_x), y + row_h * 0.55), radius=4, fill=color)
        draw.text((bar_x + (8 if smd >= 0 else -118), y - 1), f"d={smd:+.2f} ({diff:+.2f})", fill=INK, font=font(16, True))
    img.save(out_path)


def draw_top_scatter(df: pd.DataFrame, corr_rows: list[dict], out_path: Path) -> None:
    top = [row for row in corr_rows if int(row["n"]) >= 8 and row["pearson_r"] != ""][:4]
    img, draw = new_canvas(
        "Top Complete-Data Relationships",
        "Each point is one FIDAL race; y-axis is performance_score, so higher is better.",
    )
    panel_w, panel_h = 615, 280
    positions = [(70, 150), (800, 150), (70, 500), (800, 500)]
    for row, (x0, y0) in zip(top, positions, strict=False):
        x1, y1 = x0 + panel_w, y0 + panel_h
        draw.rectangle((x0, y0, x1, y1), outline=GRID, width=2)
        column = row["variable"]
        subset = df[[column, OUTCOME]].dropna()
        xs = subset[column].to_numpy(dtype=float)
        ys = subset[OUTCOME].to_numpy(dtype=float)
        draw.text((x0, y0 - 32), f"{row['label']}  r={float(row['pearson_r']):+.2f}", fill=INK, font=font(20, True))
        if len(xs) < 2:
            continue
        xmin, xmax = xs.min(), xs.max()
        ymin, ymax = ys.min(), ys.max()
        if xmin == xmax:
            xmin -= 1
            xmax += 1
        if ymin == ymax:
            ymin -= 1
            ymax += 1
        for gx in range(5):
            x = x0 + 45 + gx * (panel_w - 75) / 4
            draw.line((x, y0 + 25, x, y1 - 35), fill=GRID, width=1)
        for gy in range(5):
            y = y1 - 35 - gy * (panel_h - 65) / 4
            draw.line((x0 + 45, y, x1 - 30, y), fill=GRID, width=1)
        coords = []
        for xv, yv in zip(xs, ys, strict=False):
            px = x0 + 45 + (xv - xmin) / (xmax - xmin) * (panel_w - 75)
            py = y1 - 35 - (yv - ymin) / (ymax - ymin) * (panel_h - 65)
            coords.append((px, py))
            draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill=PINK)
        # Least-squares visual trend.
        slope, intercept = np.polyfit(xs, ys, 1)
        x_line = np.array([xmin, xmax])
        y_line = slope * x_line + intercept
        line_coords = []
        for xv, yv in zip(x_line, y_line, strict=False):
            px = x0 + 45 + (xv - xmin) / (xmax - xmin) * (panel_w - 75)
            py = y1 - 35 - (yv - ymin) / (ymax - ymin) * (panel_h - 65)
            line_coords.append((px, py))
        draw.line(line_coords, fill=BLUE, width=3)
        draw.text((x0 + 50, y1 - 28), column, fill=MUTED, font=font(14))
        draw.text((x0 + 8, y0 + 10), "perf", fill=MUTED, font=font(13))
    img.save(out_path)


def draw_best_worst_event_table(df: pd.DataFrame, out_path: Path) -> None:
    sorted_df = df.sort_values("relative_performance_pct", ascending=True)
    group_n = max(1, math.floor(len(sorted_df) * 0.25))
    best = sorted_df.head(group_n)
    worst = sorted_df.tail(group_n)
    img, draw = new_canvas(
        "Best and Worst Quartile Races",
        f"Best {group_n} and worst {group_n} races by FIDAL event-relative performance.",
    )
    headers = ["Group", "Date", "Event", "Official", "Rel %", "28d km", "Sleep 7d"]
    x_positions = [55, 190, 345, 590, 780, 940, 1120]
    y = 150
    for x, h in zip(x_positions, headers, strict=False):
        draw.text((x, y), h, fill=INK, font=font(18, True))
    y += 35
    for label, frame in [("Best", best), ("Worst", worst)]:
        for _, row in frame.iterrows():
            values = [
                label,
                str(row["race_date"])[:10],
                str(row["fidal_event"]),
                str(row["official_time_text"]),
                f"{row['relative_performance_pct']:.2f}",
                f"{row['run_km_28d']:.1f}",
                f"{row['sleep_avg_hours_7d']:.2f}",
            ]
            for x, value in zip(x_positions, values, strict=False):
                draw.text((x, y), value, fill=INK if label == "Best" else MUTED, font=font(16))
            y += 30
        y += 16
    img.save(out_path)


def markdown_table(rows: list[dict], columns: list[str], labels: list[str] | None = None, max_rows: int | None = None) -> str:
    labels = labels or columns
    shown = rows[:max_rows] if max_rows else rows
    lines = ["| " + " | ".join(labels) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in shown:
        lines.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join(lines)


def repeated_event_subset(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["fidal_event"].value_counts()
    return df[df["fidal_event"].map(counts) >= 3].copy()


def create_findings_doc(
    corr_rows: list[dict],
    quartile_rows: list[dict],
    rankings: list[dict],
    sensitivity_rows: list[dict],
    sensitivity_df: pd.DataFrame,
    df: pd.DataFrame,
) -> None:
    out = PROJECT_ROOT / "docs" / "Statistical_Findings.md"
    strongest_positive = [row for row in corr_rows if row["pearson_r"] != "" and float(row["pearson_r"]) > 0]
    strongest_negative = [row for row in corr_rows if row["pearson_r"] != "" and float(row["pearson_r"]) < 0]
    strongest_positive = sorted(strongest_positive, key=lambda row: float(row["pearson_r"]), reverse=True)
    strongest_negative = sorted(strongest_negative, key=lambda row: float(row["pearson_r"]))
    little = [row for row in corr_rows if row["pearson_r"] != "" and abs(float(row["pearson_r"])) < 0.2 and int(row["n"]) >= 8]
    n = len(df)
    best_n = max(1, math.floor(n * 0.25))
    hrv_n = int(df["hrv_avg_7d"].notna().sum())
    doc = f"""# Statistical Findings

## Methods

The primary dataset is `data/race_context_dataset.csv`, rebuilt from official FIDAL race results for 2023-2026 and matched to same-day Garmin running activities. The analysis includes {n} official races.

The outcome variable is `performance_score = -relative_performance_pct`. This makes interpretation easier: higher `performance_score` means a race was closer to the athlete's best official result within the same FIDAL event. Correlations are therefore interpreted as:

- positive correlation: higher variable values are associated with better event-relative performance;
- negative correlation: higher variable values are associated with worse event-relative performance.

For each requested Garmin-derived variable, the script calculated Pearson correlation, Spearman correlation, approximate two-sided p-values, and Fisher z 95% confidence intervals when possible. Spearman p-values use the standard large-sample t approximation on ranked data. HRV estimates are sparse and should be interpreted as descriptive only.

Best vs worst quartile comparisons use the best {best_n} and worst {best_n} races by event-relative performance.

## Dataset Notes

- Official race rows: {n}
- Garmin same-day race matches: {int((df['garmin_match_status'] == 'matched').sum())}
- Garmin missing race matches: {int((df['garmin_match_status'] != 'matched').sum())}
- Suspicious Garmin match flags: {int((df['suspicious_mismatch_flag'] == 'yes').sum())}
- 7-day HRV available for {hrv_n} races only.
- Repeated-event sensitivity rows: {len(sensitivity_df)} races from events with at least 3 imported results.

## Correlation Results

{markdown_table(corr_rows, ['label', 'n', 'pearson_r', 'pearson_p', 'pearson_ci_low', 'pearson_ci_high', 'spearman_rho', 'spearman_p', 'evidence_note'], ['Variable', 'n', 'Pearson r', 'p', 'CI low', 'CI high', 'Spearman rho', 'p', 'Evidence'])}

## Strongest Positive Associations

{markdown_table(strongest_positive, ['label', 'n', 'pearson_r', 'pearson_p', 'spearman_rho', 'evidence_note'], ['Variable', 'n', 'Pearson r', 'p', 'Spearman', 'Evidence'], max_rows=5)}

## Strongest Negative Associations

{markdown_table(strongest_negative, ['label', 'n', 'pearson_r', 'pearson_p', 'spearman_rho', 'evidence_note'], ['Variable', 'n', 'Pearson r', 'p', 'Spearman', 'Evidence'], max_rows=5)}

## Variables With Little Explanatory Value

{markdown_table(little, ['label', 'n', 'pearson_r', 'pearson_p', 'spearman_rho'], ['Variable', 'n', 'Pearson r', 'p', 'Spearman']) if little else 'No complete-data variable had an absolute Pearson correlation below 0.20.'}

## Best 25% vs Worst 25%

{markdown_table(quartile_rows, ['label', 'best_n', 'worst_n', 'best_mean', 'worst_mean', 'best_minus_worst', 'standardized_mean_difference', 'direction'], ['Variable', 'Best n', 'Worst n', 'Best mean', 'Worst mean', 'Best - worst', 'Std diff', 'Direction'])}

## Sensitivity Check: Repeated Events Only

The main dataset includes one-off events such as 800m, 5 km road, 10 km road, 30-minute run, and steeplechase. Those rows can have `relative_performance_pct = 0` because there is only one official result for that event. As a sensitivity check, the script repeated the correlation analysis on events with at least 3 official rows: 1500m, 3000m, and 5000m.

{markdown_table(sensitivity_rows, ['label', 'n', 'pearson_r', 'pearson_p', 'pearson_ci_low', 'pearson_ci_high', 'spearman_rho', 'spearman_p', 'evidence_note'], ['Variable', 'n', 'Pearson r', 'p', 'CI low', 'CI high', 'Spearman rho', 'p', 'Evidence'], max_rows=8)}

## Ranked Answer: What Appears To Matter Most?

This ranking combines absolute Pearson and Spearman signal strength, then down-weights variables with sparse coverage. It is a descriptive ranking, not a causal model.

{markdown_table(rankings, ['rank', 'label', 'signal_strength_score', 'raw_correlation_strength', 'coverage_weight', 'pearson_r', 'spearman_rho', 'n', 'quartile_best_minus_worst', 'confidence'], ['Rank', 'Variable', 'Signal', 'Raw corr strength', 'Coverage weight', 'Pearson', 'Spearman', 'n', 'Best - worst', 'Confidence'])}

## Interpretation

The strongest complete-data signals are the longer running-volume windows, especially 56-day and 28-day running volume. In this athlete's official 2023-2026 FIDAL race dataset, higher pre-race running volume is generally associated with better event-relative performance. This remains visible in the repeated-event sensitivity check, so it is not only an artifact of one-off event rows. This is consistent with the idea that sustained aerobic training volume matters for middle-distance/endurance development.

VO2max also shows a positive descriptive relationship with better event-relative performance. Because Garmin VO2max is model-derived and partly influenced by recent running performance, it should be interpreted as a fitness-context indicator rather than an independent cause.

Acute load shows weaker explanatory value than longer running-volume windows. This suggests that the short-term load number alone is less informative than the accumulated training context, at least in this dataset.

Sleep shows a time-window-dependent signal. The 7-day sleep average has little explanatory value, but 14-day and especially 28-day sleep averages show positive associations with better event-relative performance. In the repeated-event sensitivity check, 28-day sleep is the strongest single association. This should still be interpreted cautiously: sleep may reflect broader recovery, consistency, season phase, school/life load, illness, or taper context rather than acting as a simple independent cause.

HRV and RHR proxy are limited by coverage in the race-context table. They are available only for a few later races, making p-values and confidence intervals unreliable. RHR proxy also remains a wearable-derived proxy, not a controlled physiological measurement.

## Limitations

- Single-athlete observational case study; no causal inference.
- Mixed race events; `relative_performance_pct` normalizes within event but cannot remove all event-specific differences.
- Unique-event rows such as 800m, 5 km road, 10 km road, 30-minute run, and steeplechase have limited within-event comparison.
- HRV coverage is sparse.
- Garmin VO2max, acute load, HRV, sleep, and RHR proxy are consumer wearable estimates.
- Race tactics, weather, illness, injury, competition level, and taper intent are not fully controlled.
- P-values are exploratory and not corrected for multiple comparisons.

## Figures

- `figures/stat_correlation_rankings.png`
- `figures/stat_best_worst_quartile_differences.png`
- `figures/stat_top_relationships_scatter.png`
- `figures/stat_best_worst_races.png`
"""
    out.write_text(doc, encoding="utf-8")


def main() -> None:
    ensure_output_dirs()
    df = pd.read_csv(DATA_DIR / "race_context_dataset.csv")
    for column, _ in VARIABLES:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["relative_performance_pct"] = pd.to_numeric(df["relative_performance_pct"], errors="coerce")
    df[OUTCOME] = -df["relative_performance_pct"]

    corr_rows = correlation_table(df)
    quartile_rows = quartile_comparison(df)
    rankings = build_rankings(corr_rows, quartile_rows)
    sensitivity_df = repeated_event_subset(df)
    sensitivity_rows = correlation_table(sensitivity_df)

    write_csv(
        DATA_DIR / "stat_correlation_results.csv",
        corr_rows,
        [
            "variable",
            "label",
            "n",
            "pearson_r",
            "pearson_p",
            "pearson_ci_low",
            "pearson_ci_high",
            "spearman_rho",
            "spearman_p",
            "spearman_ci_low",
            "spearman_ci_high",
            "abs_pearson",
            "direction_for_better_performance",
            "evidence_note",
        ],
    )
    write_csv(
        DATA_DIR / "stat_best_worst_quartile_comparison.csv",
        quartile_rows,
        [
            "variable",
            "label",
            "best_n",
            "worst_n",
            "best_mean",
            "worst_mean",
            "best_minus_worst",
            "standardized_mean_difference",
            "direction",
        ],
    )
    write_csv(
        DATA_DIR / "stat_signal_ranking.csv",
        rankings,
        [
            "rank",
            "variable",
            "label",
            "signal_strength_score",
            "raw_correlation_strength",
            "coverage_weight",
            "pearson_r",
            "spearman_rho",
            "n",
            "quartile_best_minus_worst",
            "interpretation",
            "confidence",
        ],
    )
    write_csv(
        DATA_DIR / "stat_correlation_results_repeated_events.csv",
        sensitivity_rows,
        [
            "variable",
            "label",
            "n",
            "pearson_r",
            "pearson_p",
            "pearson_ci_low",
            "pearson_ci_high",
            "spearman_rho",
            "spearman_p",
            "spearman_ci_low",
            "spearman_ci_high",
            "abs_pearson",
            "direction_for_better_performance",
            "evidence_note",
        ],
    )

    draw_correlation_bar(corr_rows, FIGURES_DIR / "stat_correlation_rankings.png")
    draw_quartile_differences(quartile_rows, FIGURES_DIR / "stat_best_worst_quartile_differences.png")
    draw_top_scatter(df, corr_rows, FIGURES_DIR / "stat_top_relationships_scatter.png")
    draw_best_worst_event_table(df, FIGURES_DIR / "stat_best_worst_races.png")
    create_findings_doc(corr_rows, quartile_rows, rankings, sensitivity_rows, sensitivity_df, df)

    print(f"Wrote {DATA_DIR / 'stat_correlation_results.csv'}")
    print(f"Wrote {DATA_DIR / 'stat_best_worst_quartile_comparison.csv'}")
    print(f"Wrote {DATA_DIR / 'stat_signal_ranking.csv'}")
    print(f"Wrote {DATA_DIR / 'stat_correlation_results_repeated_events.csv'}")
    print(f"Wrote {PROJECT_ROOT / 'docs' / 'Statistical_Findings.md'}")
    print(f"Wrote statistical figures to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
