# FIDAL Race Import Report

Source: [FIDAL athlete profile - Andrea Bertoldo](https://www.fidal.it/atleta/BERTOLDO+Andrea/eK2Rk5OmaWM%3D)

Import date: 2026-06-04

## Summary

The FIDAL athlete profile was treated as the official race-results source of truth. The import script parsed all result tables from the public profile and saved them to:

`data/fidal_official_results.csv`

The race-context dataset was rebuilt from FIDAL official results, filtered to 2023-2026 middle-distance/endurance events useful for the Garmin case study.

| Check | Result |
|---|---:|
| FIDAL profile result rows parsed | 66 |
| Race-context rows imported | 29 |
| Years included | 2023-2026 |
| Garmin same-day matches found | 29 |
| Garmin same-day matches missing | 0 |
| Suspicious Garmin mismatches flagged | 2 |

## Events Included

Included events:

- 800 metri
- 1500 metri
- 3000 metri
- 5000 metri
- corsa km 5 strada
- Corsa strada Km 10
- Corsa 30' Allievi
- 2000 siepi H84

## Races Imported

| Date | Event | Official result | City | Garmin match | Review flag |
|---|---|---:|---|---|---|
| 2023-04-01 | 3000 metri | 10:11.12 | Venezia | matched |  |
| 2023-05-01 | 3000 metri | 10:21.75 | Padova | matched |  |
| 2023-05-13 | 1500 metri | 4:35.28 | Padova | matched |  |
| 2023-05-27 | 1500 metri | 4:30.99 | Caorle | matched |  |
| 2023-05-28 | 5000 metri | 18:13.91 | Caorle | matched |  |
| 2023-06-13 | 2000 siepi H84 | 6:52.10 | Venezia | matched |  |
| 2023-09-09 | 1500 metri | 4:22.83 | Venezia | matched |  |
| 2023-09-10 | 3000 metri | 9:43.52 | Venezia | matched |  |
| 2024-01-27 | 1500 metri | 4:30.80 | Padova | matched | yes |
| 2024-04-14 | Corsa 30' Allievi | 30:00 | Treviso | matched |  |
| 2024-06-28 | 3000 metri | 9:52.80 | San Biagio Di Callalta | matched |  |
| 2024-07-27 | 5000 metri | 16:50.28 | Domegge Di Cadore | matched |  |
| 2024-08-03 | 3000 metri | 9:18.53 | Tolmezzo | matched |  |
| 2024-09-08 | 5000 metri | 16:16.13 | Bassano Del Grappa | matched |  |
| 2024-09-15 | corsa km 5 strada | 16:31 | Pordenone | matched |  |
| 2024-10-06 | Corsa strada Km 10 | 34:14 | Arezzo | matched |  |
| 2025-01-18 | 3000 metri | 9:12.22 | Padova | matched |  |
| 2025-02-09 | 3000 metri | 9:06.25 | Padova | matched | yes |
| 2025-05-10 | 1500 metri | 4:25.56 | San Biagio Di Callalta | matched |  |
| 2025-05-24 | 1500 metri | 4:23.47 | Valeggio Sul Mincio | matched |  |
| 2025-06-29 | 5000 metri | 16:02.66 | Scorze' | matched |  |
| 2025-07-23 | 1500 metri | 4:10.61 | Montebelluna | matched |  |
| 2025-08-23 | 800 metri | 2:05.66 | Cles | matched |  |
| 2025-09-06 | 1500 metri | 4:15.27 | Bassano Del Grappa | matched |  |
| 2025-09-07 | 5000 metri | 15:59.98 | Bassano Del Grappa | matched |  |
| 2025-09-28 | 5000 metri | 15:54.20 | Trieste | matched |  |
| 2026-05-01 | 3000 metri | 9:11.10 | Este | matched |  |
| 2026-05-17 | 5000 metri | 15:54.63 | Conegliano | matched |  |
| 2026-05-30 | 5000 metri | 15:43.94 | Borgo Valbelluna | matched |  |

## Races Excluded

37 FIDAL profile rows were excluded from `race_context_dataset.csv`.

Exclusion logic:

- Exclude pre-2023 races to keep the paper focused on the Garmin-era middle-distance/endurance build.
- Exclude childhood or non-endurance events not needed for this analysis.
- Exclude field and multi-event results because the race-context dataset is built around timed running/race-walk performance.

Excluded 2023-2026 rows:

| Date | Event | Result | City | Reason |
|---|---|---:|---|---|
| 2023-04-29 | 400 metri | 59.03 | San Biagio Di Callalta | Sprint; outside current middle-distance/endurance scope. |
| 2024-04-07 | 500 metri | 1:13.94 | Mestre | Short sprint/middle transition event; outside current priority event list. |

Older excluded rows were mainly 2019-2022 youth/childhood results, 1000m/2000m cadet races, hurdles, field events, race walk, vortex, and tetrathlon.

## Garmin Matching Method

For each imported FIDAL race, the script searched Garmin summarized activities on the same calendar date and kept only running activities. If multiple Garmin runs existed on the same day, it selected the activity with the smallest combined difference from the official race distance and official race duration.

No Garmin activity IDs, coordinates, device IDs, GPS traces, or raw locations are stored in the dataset.

## Garmin Matches Found

All 29 imported FIDAL races had a same-day Garmin running activity match.

This does not mean every match is perfect. It means there was at least one same-day Garmin run and the selected activity was the closest by distance and duration.

## Garmin Matches Missing

No missing same-day Garmin matches were found for the imported 2023-2026 target races.

## Suspicious Mismatches

Two matches were flagged for manual review:

| Date | Event | Official result | Garmin distance | Garmin moving duration | Delta distance | Delta time | Possible explanation |
|---|---|---:|---:|---:|---:|---:|---|
| 2024-01-27 | 1500 metri | 4:30.80 | 0.979 km | 5.57 min | -521 m | +63.40 s | Garmin may have recorded only part of the race, warmup/cooldown, or an indoor/track distance issue. |
| 2025-02-09 | 3000 metri | 9:06.25 | 3.136 km | 14.73 min | +136 m | +337.55 s | Garmin duration likely includes extra time beyond the official race, such as warmup, cooldown, waiting, or recording not stopped. |

These rows are still kept because FIDAL is the official result source. Garmin match fields should be treated as wearable context, not official performance ground truth.

## Output Files Updated

- `data/fidal_official_results.csv`
- `data/race_context_dataset.csv`
- `figures/*.png`
- `scripts/build_official_race_list.py`
- `scripts/build_race_context_dataset.py`

## Manual Checks Still Recommended

- Confirm whether the two suspicious Garmin matches should be manually overridden or left as flagged.
- Add weather, tactical, illness, and injury notes where known.
- Decide whether to include 1000m/2000m youth results in a separate historical appendix, outside the main research dataset.
