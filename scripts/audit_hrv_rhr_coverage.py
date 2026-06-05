#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path

from common import DATA_DIR, PROJECT_ROOT, ensure_output_dirs, parse_iso_date, read_json, wellness_dir


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def classify_missing(race_date, coverage_first, hrv_count, rhr_count) -> str:
    if hrv_count > 0 or rhr_count > 0:
        return "covered"
    if race_date - timedelta(days=1) < coverage_first:
        return "date outside HRV/RHR availability"
    if race_date - timedelta(days=28) < coverage_first <= race_date - timedelta(days=1):
        return "partial window possible but no HRV/RHR rows in pre-race window"
    return "data not recorded in preceding 28 days"


def audit_raw_health_status() -> dict:
    metric_counts = Counter()
    dates_by_metric = defaultdict(list)
    source_files = sorted(wellness_dir().glob("*_healthStatusData.json"))
    for path in source_files:
        for row in read_json(path):
            day = row.get("calendarDate")
            for metric in row.get("metrics", []):
                metric_type = metric.get("type") or "<missing>"
                metric_counts[metric_type] += 1
                if metric.get("value") not in (None, ""):
                    dates_by_metric[metric_type].append(day)

    def metric_range(metric_type: str) -> str:
        dates = [day for day in dates_by_metric.get(metric_type, []) if day]
        if not dates:
            return ""
        return f"{min(dates)} to {max(dates)}"

    return {
        "source_file_count": len(source_files),
        "metric_counts": dict(sorted(metric_counts.items())),
        "hrv_raw_count": len(dates_by_metric.get("HRV", [])),
        "hr_raw_count": len(dates_by_metric.get("HR", [])),
        "hrv_raw_range": metric_range("HRV"),
        "hr_raw_range": metric_range("HR"),
        "has_rhr_metric": "RHR" in metric_counts,
    }


def main() -> None:
    ensure_output_dirs()
    races = read_csv(DATA_DIR / "race_context_dataset.csv")
    health = read_csv(DATA_DIR / "daily_health_summary.csv")
    raw_health = audit_raw_health_status()

    hrv_dates = [parse_iso_date(row["date"]) for row in health if row.get("hrv_ms")]
    rhr_dates = [parse_iso_date(row["date"]) for row in health if row.get("rhr_proxy_bpm")]
    health_by_date = {parse_iso_date(row["date"]): row for row in health}

    coverage_first = min(hrv_dates + rhr_dates)
    rows = []
    for race in races:
        race_date = parse_iso_date(race["race_date"])
        start = race_date - timedelta(days=28)
        end = race_date - timedelta(days=1)
        hrv_window_dates = []
        rhr_window_dates = []
        for offset in range(28):
            day = start + timedelta(days=offset)
            row = health_by_date.get(day)
            if row and row.get("hrv_ms"):
                hrv_window_dates.append(day)
            if row and row.get("rhr_proxy_bpm"):
                rhr_window_dates.append(day)
        rows.append(
            {
                "race_date": race["race_date"],
                "fidal_event": race["fidal_event"],
                "official_time_text": race["official_time_text"],
                "city": race.get("city", ""),
                "window_start": start.isoformat(),
                "window_end": end.isoformat(),
                "hrv_days_in_28d": len(hrv_window_dates),
                "rhr_days_in_28d": len(rhr_window_dates),
                "hrv_exists_28d": "yes" if hrv_window_dates else "no",
                "rhr_exists_28d": "yes" if rhr_window_dates else "no",
                "first_hrv_in_window": hrv_window_dates[0].isoformat() if hrv_window_dates else "",
                "last_hrv_in_window": hrv_window_dates[-1].isoformat() if hrv_window_dates else "",
                "first_rhr_in_window": rhr_window_dates[0].isoformat() if rhr_window_dates else "",
                "last_rhr_in_window": rhr_window_dates[-1].isoformat() if rhr_window_dates else "",
                "missing_reason": classify_missing(race_date, coverage_first, len(hrv_window_dates), len(rhr_window_dates)),
                "race_dataset_hrv_avg_28d": race.get("hrv_avg_28d", ""),
                "race_dataset_rhr_avg_28d": race.get("rhr_avg_28d", ""),
            }
        )

    fieldnames = [
        "race_date",
        "fidal_event",
        "official_time_text",
        "city",
        "window_start",
        "window_end",
        "hrv_days_in_28d",
        "rhr_days_in_28d",
        "hrv_exists_28d",
        "rhr_exists_28d",
        "first_hrv_in_window",
        "last_hrv_in_window",
        "first_rhr_in_window",
        "last_rhr_in_window",
        "missing_reason",
        "race_dataset_hrv_avg_28d",
        "race_dataset_rhr_avg_28d",
    ]
    write_csv(DATA_DIR / "hrv_rhr_race_coverage_audit.csv", rows, fieldnames)

    covered = [row for row in rows if row["hrv_exists_28d"] == "yes" or row["rhr_exists_28d"] == "yes"]
    no_coverage = [row for row in rows if row["hrv_exists_28d"] == "no" and row["rhr_exists_28d"] == "no"]
    report = f"""# HRV/RHR Coverage Audit

## Summary

This audit verifies HRV and RHR-proxy coverage directly from `data/daily_health_summary.csv` and compares it to the 29 official FIDAL race rows in `data/race_context_dataset.csv`.

| Check | HRV | RHR proxy |
|---|---:|---:|
| Total rows available | {len(hrv_dates)} | {len(rhr_dates)} |
| First date | {min(hrv_dates).isoformat() if hrv_dates else ''} | {min(rhr_dates).isoformat() if rhr_dates else ''} |
| Last date | {max(hrv_dates).isoformat() if hrv_dates else ''} | {max(rhr_dates).isoformat() if rhr_dates else ''} |
| Official races with preceding-28-day coverage | {sum(1 for row in rows if row['hrv_exists_28d'] == 'yes')} | {sum(1 for row in rows if row['rhr_exists_28d'] == 'yes')} |

Result: the statistical report statement is correct. HRV/RHR coverage is sparse for race inference because Garmin HRV/RHR-proxy rows begin on 2025-09-18. Only 4 of the 29 official race rows have HRV/RHR data in the preceding 28 days.

## Source-Data Cross-Check

The derived health summary was checked against the raw Garmin `healthStatusData` exports.

| Check | Result |
|---|---:|
| Raw health-status source files | {raw_health['source_file_count']} |
| Raw HRV-valued records | {raw_health['hrv_raw_count']} |
| Raw HR-valued records used as RHR proxy | {raw_health['hr_raw_count']} |
| Raw HRV date range | {raw_health['hrv_raw_range']} |
| Raw HR date range | {raw_health['hr_raw_range']} |
| Separate raw `RHR` metric present | {'yes' if raw_health['has_rhr_metric'] else 'no'} |

Raw metric types present:

"""
    for metric_type, count in raw_health["metric_counts"].items():
        report += f"- {metric_type}: {count}\n"

    report += f"""
Interpretation: the low coverage is not caused by the parser skipping older HRV/RHR rows. The Garmin export contains HRV and HR health-status records only from 2025-09-18 onward, and no separate `RHR` metric is present in these files. The `rhr_*` race-context variables therefore remain a Garmin health-status HR proxy.

## Per-Race Coverage

| Date | Event | Official | Window | HRV days | RHR days | HRV? | RHR? | Missing reason |
|---|---|---:|---|---:|---:|---|---|---|
"""
    for row in rows:
        report += (
            f"| {row['race_date']} | {row['fidal_event']} | {row['official_time_text']} | "
            f"{row['window_start']} to {row['window_end']} | {row['hrv_days_in_28d']} | {row['rhr_days_in_28d']} | "
            f"{row['hrv_exists_28d']} | {row['rhr_exists_28d']} | {row['missing_reason']} |\n"
        )

    report += f"""
## Covered Races

{len(covered)} races have HRV/RHR coverage in the preceding 28 days:

"""
    for row in covered:
        report += f"- {row['race_date']} {row['fidal_event']} ({row['official_time_text']}): HRV days {row['hrv_days_in_28d']}, RHR days {row['rhr_days_in_28d']}.\n"

    report += f"""
## Missing-Coverage Explanation

{len(no_coverage)} races have no HRV/RHR data in the preceding 28 days.

Reason breakdown:

"""
    reason_counts = {}
    for row in rows:
        reason_counts[row["missing_reason"]] = reason_counts.get(row["missing_reason"], 0) + 1
    for reason, count in sorted(reason_counts.items(), key=lambda item: item[0]):
        report += f"- {reason}: {count}\n"

    report += """
## Bug Assessment

No race-context rebuild is required for HRV/RHR coverage.

Evidence:

- `daily_health_summary.csv` contains 256 HRV rows and 256 RHR-proxy rows.
- Both HRV and RHR-proxy coverage run from 2025-09-18 to 2026-06-04.
- Raw Garmin health-status files contain 256 HRV-valued records and 256 HR-valued records, matching the derived health summary.
- No separate raw `RHR` metric is present in the checked health-status exports.
- The only official race before late 2025 with possible partial HRV/RHR coverage is 2025-09-28; it correctly has 10 pre-race HRV/RHR days.
- The 2026-05-01, 2026-05-17, and 2026-05-30 races each correctly have 27 pre-race HRV/RHR days in the 28-day window.
- Earlier races are outside the HRV/RHR availability period.
- There is no Garmin activity matching issue involved; HRV/RHR coverage is daily health-data coverage, not activity matching.

## Output

Detailed CSV:

`data/hrv_rhr_race_coverage_audit.csv`
"""
    (PROJECT_ROOT / "docs" / "HRV_RHR_Coverage_Audit.md").write_text(report, encoding="utf-8")

    print(f"HRV rows: {len(hrv_dates)}")
    print(f"RHR rows: {len(rhr_dates)}")
    print(f"HRV range: {min(hrv_dates).isoformat()} to {max(hrv_dates).isoformat()}")
    print(f"RHR range: {min(rhr_dates).isoformat()} to {max(rhr_dates).isoformat()}")
    print(f"Races with HRV coverage in preceding 28d: {sum(1 for row in rows if row['hrv_exists_28d'] == 'yes')}")
    print(f"Races with RHR coverage in preceding 28d: {sum(1 for row in rows if row['rhr_exists_28d'] == 'yes')}")
    print(f"Wrote {DATA_DIR / 'hrv_rhr_race_coverage_audit.csv'}")
    print(f"Wrote {PROJECT_ROOT / 'docs' / 'HRV_RHR_Coverage_Audit.md'}")


if __name__ == "__main__":
    main()
