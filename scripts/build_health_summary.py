#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import defaultdict

from common import DATA_DIR, date_from_any, ensure_output_dirs, read_json, round_float, wellness_dir


def write_csv(path, rows, fieldnames) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ensure_output_dirs()
    daily = defaultdict(dict)

    for path in sorted(wellness_dir().glob("*_sleepData.json")):
        for row in read_json(path):
            day = date_from_any(row.get("calendarDate"))
            if day is None:
                continue
            sleep_seconds = sum(float(row.get(key) or 0) for key in ("deepSleepSeconds", "lightSleepSeconds", "remSleepSeconds"))
            daily[day.isoformat()].update(
                {
                    "sleep_hours": round(sleep_seconds / 3600, 2),
                    "awake_sleep_hours": round(float(row.get("awakeSleepSeconds") or 0) / 3600, 2),
                    "sleep_score": row.get("sleepScores", {}).get("overallScore"),
                    "sleep_avg_stress": round_float(row.get("avgSleepStress"), 1),
                }
            )

    for path in sorted(wellness_dir().glob("*_healthStatusData.json")):
        for row in read_json(path):
            day = date_from_any(row.get("calendarDate"))
            if day is None:
                continue
            out = daily[day.isoformat()]
            for metric in row.get("metrics", []):
                metric_type = metric.get("type")
                if metric_type == "HRV":
                    out["hrv_ms"] = round_float(metric.get("value"), 1)
                    out["hrv_status"] = metric.get("status") or ""
                elif metric_type == "HR":
                    out["rhr_proxy_bpm"] = round_float(metric.get("value"), 1)
                    out["rhr_proxy_status"] = metric.get("status") or ""

    rows = []
    for day in sorted(daily):
        values = daily[day]
        rows.append(
            {
                "date": day,
                "sleep_hours": values.get("sleep_hours"),
                "awake_sleep_hours": values.get("awake_sleep_hours"),
                "sleep_score": values.get("sleep_score"),
                "sleep_avg_stress": values.get("sleep_avg_stress"),
                "hrv_ms": values.get("hrv_ms"),
                "hrv_status": values.get("hrv_status", ""),
                "rhr_proxy_bpm": values.get("rhr_proxy_bpm"),
                "rhr_proxy_status": values.get("rhr_proxy_status", ""),
                "sleep_need_hours": "",
            }
        )

    write_csv(
        DATA_DIR / "daily_health_summary.csv",
        rows,
        [
            "date",
            "sleep_hours",
            "awake_sleep_hours",
            "sleep_score",
            "sleep_avg_stress",
            "hrv_ms",
            "hrv_status",
            "rhr_proxy_bpm",
            "rhr_proxy_status",
            "sleep_need_hours",
        ],
    )
    print(f"Wrote {DATA_DIR / 'daily_health_summary.csv'}")
    print(f"Daily health rows: {len(rows)}")


if __name__ == "__main__":
    main()
