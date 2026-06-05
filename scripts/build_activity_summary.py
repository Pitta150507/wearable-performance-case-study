#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import defaultdict

from common import DATA_DIR, ensure_output_dirs, fitness_export_dir, garmin_local_date, read_json, round_float


RUN_TYPES = {"running", "track_running", "treadmill_running", "trail_running", "indoor_running"}
BIKE_TYPES = {"cycling", "mountain_biking", "indoor_cycling", "e_bike_fitness"}


def classify_activity(activity_type: str | None, sport_type: str | None) -> str:
    activity = (activity_type or "").lower()
    sport = (sport_type or "").upper()
    if activity in RUN_TYPES or sport == "RUNNING":
        return "run"
    if activity in BIKE_TYPES or sport == "CYCLING":
        return "bike"
    return "other"


def iter_activities() -> list[dict]:
    rows = []
    for path in sorted(fitness_export_dir().glob("*summarizedActivities.json")):
        payload = read_json(path)
        records = payload[0].get("summarizedActivitiesExport", []) if payload else []
        for record in records:
            local_ms = record.get("startTimeLocal") or record.get("beginTimestamp")
            activity_date = garmin_local_date(local_ms)
            if activity_date is None:
                continue
            activity_type = record.get("activityType")
            sport_type = record.get("sportType")
            category = classify_activity(activity_type, sport_type)
            distance_km = round_float((record.get("distance") or 0) / 100000, 3)
            duration_min = round_float((record.get("duration") or 0) / 60000, 2)
            moving_duration_min = round_float((record.get("movingDuration") or record.get("duration") or 0) / 60000, 2)
            rows.append(
                {
                    "activity_date": activity_date.isoformat(),
                    "activity_category": category,
                    "activity_type": activity_type or "",
                    "sport_type": sport_type or "",
                    "distance_km": distance_km,
                    "duration_min": duration_min,
                    "moving_duration_min": moving_duration_min,
                    "avg_hr": round_float(record.get("avgHr"), 1),
                    "max_hr": round_float(record.get("maxHr"), 1),
                    "training_load": round_float(record.get("activityTrainingLoad"), 1),
                    "aerobic_training_effect": round_float(record.get("aerobicTrainingEffect"), 1),
                    "anaerobic_training_effect": round_float(record.get("anaerobicTrainingEffect"), 1),
                    "_dedupe_key": (
                        str(local_ms),
                        activity_type or "",
                        str(round(record.get("distance") or 0, 1)),
                        str(round(record.get("duration") or 0, 1)),
                    ),
                }
            )
    return rows


def write_csv(path, rows, fieldnames) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ensure_output_dirs()
    rows = iter_activities()
    seen = set()
    deduped = []
    duplicates = []
    for row in sorted(rows, key=lambda x: (x["activity_date"], x["_dedupe_key"])):
        key = row["_dedupe_key"]
        clean = {k: v for k, v in row.items() if not k.startswith("_")}
        if key in seen:
            duplicates.append(clean)
            continue
        seen.add(key)
        deduped.append(clean)

    activity_fields = [
        "activity_date",
        "activity_category",
        "activity_type",
        "sport_type",
        "distance_km",
        "duration_min",
        "moving_duration_min",
        "avg_hr",
        "max_hr",
        "training_load",
        "aerobic_training_effect",
        "anaerobic_training_effect",
    ]
    write_csv(DATA_DIR / "activity_summary.csv", deduped, activity_fields)
    write_csv(DATA_DIR / "activity_duplicate_check.csv", duplicates, activity_fields)

    daily = defaultdict(lambda: defaultdict(float))
    for row in deduped:
        day = row["activity_date"]
        category = row["activity_category"]
        duration = float(row["moving_duration_min"] or row["duration_min"] or 0)
        distance = float(row["distance_km"] or 0)
        daily[day]["total_training_duration_min"] += duration
        daily[day]["activity_count"] += 1
        if category == "run":
            daily[day]["run_km"] += distance
            daily[day]["run_duration_min"] += duration
            daily[day]["run_count"] += 1
        elif category == "bike":
            daily[day]["bike_km"] += distance
            daily[day]["bike_duration_min"] += duration
            daily[day]["bike_count"] += 1

    daily_rows = []
    for day, values in sorted(daily.items()):
        daily_rows.append(
            {
                "date": day,
                "run_km": round(values["run_km"], 3),
                "run_duration_min": round(values["run_duration_min"], 2),
                "run_count": int(values["run_count"]),
                "bike_km": round(values["bike_km"], 3),
                "bike_duration_min": round(values["bike_duration_min"], 2),
                "bike_count": int(values["bike_count"]),
                "total_training_duration_min": round(values["total_training_duration_min"], 2),
                "activity_count": int(values["activity_count"]),
            }
        )
    write_csv(
        DATA_DIR / "daily_training_summary.csv",
        daily_rows,
        [
            "date",
            "run_km",
            "run_duration_min",
            "run_count",
            "bike_km",
            "bike_duration_min",
            "bike_count",
            "total_training_duration_min",
            "activity_count",
        ],
    )

    print(f"Activities read: {len(rows)}")
    print(f"Deduplicated activities: {len(deduped)}")
    print(f"Potential duplicates: {len(duplicates)}")
    print(f"Wrote {DATA_DIR / 'activity_summary.csv'}")
    print(f"Wrote {DATA_DIR / 'daily_training_summary.csv'}")


if __name__ == "__main__":
    main()
