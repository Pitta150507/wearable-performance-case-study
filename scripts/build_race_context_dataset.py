#!/usr/bin/env python3
from __future__ import annotations

import csv
from datetime import timedelta
from pathlib import Path
from statistics import mean

from common import (
    DATA_DIR,
    date_from_any,
    ensure_output_dirs,
    fitness_dir,
    parse_iso_date,
    pre_race_window,
    read_json,
    round_float,
)


WINDOWS = (7, 14, 28, 56)
MIN_IMPORT_YEAR = 2023
TARGET_EVENTS = {
    "800 metri",
    "1500 metri",
    "3000 metri",
    "5000 metri",
    "corsa km 5 strada",
    "Corsa strada Km 10",
    "Corsa 30' Allievi",
    "2000 siepi H84",
}


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def num(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def text(value) -> str:
    return "" if value is None else str(value)


def avg(values):
    cleaned = [float(v) for v in values if v not in (None, "")]
    return round(mean(cleaned), 2) if cleaned else ""


def sum_window(rows: list[dict], race_date, days: int, field: str) -> float | str:
    start, end = pre_race_window(race_date, days)
    total = 0.0
    found = False
    for row in rows:
        day = parse_iso_date(row["date"])
        if start <= day <= end:
            value = num(row.get(field))
            if value is not None:
                total += value
                found = True
    return round(total, 2) if found else ""


def avg_window(rows: list[dict], race_date, days: int, field: str) -> float | str:
    start, end = pre_race_window(race_date, days)
    values = []
    for row in rows:
        day = parse_iso_date(row["date"])
        if start <= day <= end:
            value = num(row.get(field))
            if value is not None:
                values.append(value)
    return avg(values)


def load_official_races() -> list[dict]:
    path = DATA_DIR / "fidal_official_results.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run scripts/build_official_race_list.py before building the race context dataset."
        )
    rows = []
    for row in read_csv(path):
        year = parse_iso_date(row["race_date"]).year
        if year < MIN_IMPORT_YEAR:
            continue
        if row.get("fidal_event") not in TARGET_EVENTS:
            continue
        if row.get("include_in_race_context") != "yes":
            continue
        rows.append(row)
    return sorted(rows, key=lambda row: (row["race_date"], row.get("fidal_event", ""), row.get("official_time_seconds", "")))


def match_garmin_activity(activities: list[dict], race: dict) -> dict:
    race_day = race["race_date"]
    official_distance_m = num(race.get("distance_m"))
    official_seconds = num(race.get("official_time_seconds"))
    candidates = [
        row
        for row in activities
        if row.get("activity_date") == race_day and row.get("activity_category") == "run"
    ]
    if not candidates:
        return {
            "garmin_match_status": "missing",
            "garmin_match_notes": "No Garmin running activity found on the official race date.",
        }

    scored = []
    for row in candidates:
        garmin_distance_m = (num(row.get("distance_km")) or 0) * 1000
        garmin_seconds = (num(row.get("moving_duration_min")) or num(row.get("duration_min")) or 0) * 60
        distance_delta = abs(garmin_distance_m - official_distance_m) if official_distance_m else 0
        time_delta = abs(garmin_seconds - official_seconds) if official_seconds else 0
        distance_score = distance_delta / max(official_distance_m or 1, 1)
        time_score = time_delta / max(official_seconds or 1, 1)
        scored.append((distance_score + time_score, distance_delta, time_delta, row))

    _, distance_delta, time_delta, best = sorted(scored, key=lambda item: item[:3])[0]
    garmin_distance_m = (num(best.get("distance_km")) or 0) * 1000
    garmin_seconds = (num(best.get("moving_duration_min")) or num(best.get("duration_min")) or 0) * 60
    status = "matched"
    notes = "Best same-day Garmin run selected by distance and duration closeness."
    suspicious = ""
    if official_distance_m and distance_delta > max(150, official_distance_m * 0.08):
        suspicious = "yes"
    if official_seconds and time_delta > max(45, official_seconds * 0.08):
        suspicious = "yes"
    if suspicious:
        notes += " Distance or duration differs enough to require manual review."

    return {
        "garmin_match_status": status,
        "garmin_activity_type": best.get("activity_type", ""),
        "garmin_sport_type": best.get("sport_type", ""),
        "garmin_distance_km": round_float(best.get("distance_km"), 3),
        "garmin_moving_duration_min": round_float(best.get("moving_duration_min"), 2),
        "garmin_time_seconds": round_float(garmin_seconds, 2),
        "garmin_distance_delta_m": round_float(garmin_distance_m - (official_distance_m or 0), 1),
        "garmin_time_delta_seconds": round_float(garmin_seconds - (official_seconds or 0), 2),
        "garmin_pace_sec_per_km": round_float(garmin_seconds / (garmin_distance_m / 1000), 2) if garmin_distance_m else "",
        "suspicious_mismatch_flag": suspicious,
        "garmin_match_notes": notes,
    }


def load_metric_series() -> dict[str, list[dict]]:
    series = {
        "acute_load": [],
        "training_status": [],
        "vo2max": [],
        "race_predictions": [],
    }
    for path in sorted(fitness_dir().glob("MetricsAcuteTrainingLoad_*.json")):
        for row in read_json(path):
            day = date_from_any(row.get("calendarDate"))
            if day:
                series["acute_load"].append(
                    {
                        "date": day.isoformat(),
                        "acute_load": row.get("dailyTrainingLoadAcute"),
                        "acwr_status": row.get("acwrStatus") or "",
                    }
                )
    for path in sorted(fitness_dir().glob("TrainingHistory_*.json")):
        for row in read_json(path):
            day = date_from_any(row.get("calendarDate"))
            if day:
                series["training_status"].append(
                    {
                        "date": day.isoformat(),
                        "training_status": row.get("trainingStatus") or "",
                        "fitness_level_trend": row.get("fitnessLevelTrend") or "",
                    }
                )
    for path in sorted(fitness_dir().glob("MetricsMaxMetData_*.json")):
        for row in read_json(path):
            if row.get("sport") != "RUNNING":
                continue
            day = date_from_any(row.get("calendarDate"))
            if day:
                series["vo2max"].append({"date": day.isoformat(), "vo2max": row.get("vo2MaxValue")})
    for path in sorted(fitness_dir().glob("RunRacePredictions_*.json")):
        for row in read_json(path):
            day = date_from_any(row.get("calendarDate"))
            if day:
                series["race_predictions"].append(
                    {
                        "date": day.isoformat(),
                        "race_prediction_5k": row.get("raceTime5K"),
                        "race_prediction_10k": row.get("raceTime10K"),
                    }
                )

    for key, rows in series.items():
        latest_by_date = {}
        for row in rows:
            latest_by_date[row["date"]] = row
        series[key] = [latest_by_date[day] for day in sorted(latest_by_date)]
    return series


def nearest_prior(rows: list[dict], race_date, max_lookback_days: int = 30) -> dict:
    cutoff = race_date - timedelta(days=1)
    candidates = []
    for row in rows:
        day = parse_iso_date(row["date"])
        if day <= cutoff and (cutoff - day).days <= max_lookback_days:
            candidates.append((day, row))
    return sorted(candidates, key=lambda x: x[0])[-1][1] if candidates else {}


def pace_text(seconds: float, distance_m: int) -> float:
    return seconds / (distance_m / 1000)


def main() -> None:
    ensure_output_dirs()
    official_races = load_official_races()
    activity_rows = read_csv(DATA_DIR / "activity_summary.csv")
    training_rows = read_csv(DATA_DIR / "daily_training_summary.csv")
    health_rows = read_csv(DATA_DIR / "daily_health_summary.csv")
    metrics = load_metric_series()

    best_pace_by_event = {}
    for race in official_races:
        distance = num(race.get("distance_m"))
        official = num(race.get("official_time_seconds"))
        if distance and official:
            pace = official / (distance / 1000)
            event = race.get("fidal_event", "")
            best_pace_by_event[event] = min(best_pace_by_event.get(event, float("inf")), pace)

    prior_best_by_event = {}
    output_rows = []
    for race in sorted(official_races, key=lambda x: x["race_date"]):
        race_day = parse_iso_date(race["race_date"])
        distance = int(float(race["distance_m"]))
        official = float(race["official_time_seconds"])
        event = race.get("fidal_event", "")
        pace = pace_text(official, distance)
        prior_best = prior_best_by_event.get(event)
        best_pace = best_pace_by_event.get(event)

        row = {
            "athlete_id": race["athlete_id"],
            "race_date": race["race_date"],
            "race_name": race["race_name"],
            "fidal_event": event,
            "distance_m": distance,
            "official_time_seconds": official,
            "official_time_text": race["official_time_text"],
            "official_performance_raw": race.get("official_performance_raw", ""),
            "surface_type": race.get("surface_type", ""),
            "timing_type": race.get("timing_type", ""),
            "category": race.get("category", ""),
            "placement": race.get("placement", ""),
            "city": race.get("city", ""),
            "source": race["source"],
            "source_url": race.get("source_url", ""),
            "analysis_scope": race.get("analysis_scope", ""),
            "notes": race.get("notes", ""),
            "pb_at_distance_seconds": round_float(prior_best, 2) if prior_best is not None else "",
            "relative_performance_pct": round_float(((pace / best_pace) - 1) * 100, 2) if best_pace else "",
            "pace_sec_per_km": round_float(pace, 2),
        }
        row.update(match_garmin_activity(activity_rows, row))

        for days in WINDOWS:
            row[f"run_km_{days}d"] = sum_window(training_rows, race_day, days, "run_km")
            row[f"run_duration_min_{days}d"] = sum_window(training_rows, race_day, days, "run_duration_min")
        row["bike_duration_min_7d"] = sum_window(training_rows, race_day, 7, "bike_duration_min")
        row["bike_duration_min_28d"] = sum_window(training_rows, race_day, 28, "bike_duration_min")
        row["total_training_duration_min_7d"] = sum_window(training_rows, race_day, 7, "total_training_duration_min")
        row["total_training_duration_min_28d"] = sum_window(training_rows, race_day, 28, "total_training_duration_min")

        for days in (7, 14, 28):
            row[f"sleep_avg_hours_{days}d"] = avg_window(health_rows, race_day, days, "sleep_hours")
            row[f"sleep_need_avg_hours_{days}d"] = avg_window(health_rows, race_day, days, "sleep_need_hours")
            row[f"hrv_avg_{days}d"] = avg_window(health_rows, race_day, days, "hrv_ms")
            row[f"rhr_avg_{days}d"] = avg_window(health_rows, race_day, days, "rhr_proxy_bpm")

        nearest_vo2 = nearest_prior(metrics["vo2max"], race_day, 60)
        nearest_load = nearest_prior(metrics["acute_load"], race_day, 30)
        nearest_status = nearest_prior(metrics["training_status"], race_day, 30)
        nearest_pred = nearest_prior(metrics["race_predictions"], race_day, 30)
        row["vo2max_nearest"] = nearest_vo2.get("vo2max", "")
        row["acute_load_nearest"] = nearest_load.get("acute_load", "")
        row["training_status_nearest"] = nearest_status.get("training_status", "")
        row["race_prediction_5k_nearest"] = nearest_pred.get("race_prediction_5k", "")
        row["race_prediction_10k_nearest"] = nearest_pred.get("race_prediction_10k", "")

        row["injury_flag"] = ""
        row["injury_notes"] = "No race-specific injury note found in the current vault. A 2026 lower-leg issue is documented, but dates are not precise enough to attach to this race."
        row["heat_or_weather_notes"] = ""
        row["tactical_race_flag"] = ""
        row["confidence_level"] = race.get("confidence_level", "high")

        output_rows.append(row)
        if prior_best is None or official < prior_best:
            prior_best_by_event[event] = official

    fieldnames = [
        "athlete_id",
        "race_date",
        "race_name",
        "fidal_event",
        "distance_m",
        "official_time_seconds",
        "official_time_text",
        "official_performance_raw",
        "surface_type",
        "timing_type",
        "category",
        "placement",
        "city",
        "source",
        "source_url",
        "analysis_scope",
        "notes",
        "pb_at_distance_seconds",
        "relative_performance_pct",
        "pace_sec_per_km",
        "garmin_match_status",
        "garmin_activity_type",
        "garmin_sport_type",
        "garmin_distance_km",
        "garmin_moving_duration_min",
        "garmin_time_seconds",
        "garmin_distance_delta_m",
        "garmin_time_delta_seconds",
        "garmin_pace_sec_per_km",
        "suspicious_mismatch_flag",
        "garmin_match_notes",
        "run_km_7d",
        "run_km_14d",
        "run_km_28d",
        "run_km_56d",
        "run_duration_min_7d",
        "run_duration_min_14d",
        "run_duration_min_28d",
        "run_duration_min_56d",
        "bike_duration_min_7d",
        "bike_duration_min_28d",
        "total_training_duration_min_7d",
        "total_training_duration_min_28d",
        "sleep_avg_hours_7d",
        "sleep_avg_hours_14d",
        "sleep_avg_hours_28d",
        "sleep_need_avg_hours_7d",
        "sleep_need_avg_hours_14d",
        "sleep_need_avg_hours_28d",
        "hrv_avg_7d",
        "hrv_avg_14d",
        "hrv_avg_28d",
        "rhr_avg_7d",
        "rhr_avg_14d",
        "rhr_avg_28d",
        "vo2max_nearest",
        "acute_load_nearest",
        "training_status_nearest",
        "race_prediction_5k_nearest",
        "race_prediction_10k_nearest",
        "injury_flag",
        "injury_notes",
        "heat_or_weather_notes",
        "tactical_race_flag",
        "confidence_level",
    ]
    write_csv(DATA_DIR / "race_context_dataset.csv", output_rows, fieldnames)
    print(f"Wrote {DATA_DIR / 'race_context_dataset.csv'}")
    print(f"Race rows: {len(output_rows)}")
    print(f"Garmin matched rows: {sum(1 for row in output_rows if row.get('garmin_match_status') == 'matched')}")
    print(f"Garmin missing rows: {sum(1 for row in output_rows if row.get('garmin_match_status') == 'missing')}")
    print(f"Suspicious Garmin mismatches: {sum(1 for row in output_rows if row.get('suspicious_mismatch_flag') == 'yes')}")


if __name__ == "__main__":
    main()
