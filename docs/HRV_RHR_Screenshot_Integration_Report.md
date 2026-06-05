# HRV/RHR Screenshot Integration Report

## Summary

The screenshots were integrated as secondary/manual evidence. The Garmin export remains the primary source for exact HRV/RHR-proxy values. Screenshot-derived values are graph-digitized estimates and are not treated as equal-quality replacements for export JSON.

| Metric | Garmin export exact days | Screenshot digitized date-points | Overlap date-points | Mismatch date-points | Missing date-points recovered from screenshots |
|---|---:|---:|---:|---:|---:|
| HRV | 256 | 1331 | 254 | 115 | 1077 |
| RHR proxy/resting HR | 256 | 198 | 36 | 35 | 162 |

Important interpretation:

- HRV screenshots mostly show Garmin `HRV Status` 4-week graphs. The extracted values are approximate graph points, likely representing Garmin 7-day HRV status values rather than raw nightly HRV.
- RHR screenshots show annual heart-rate graphs. The blue series is digitized as approximate weekly resting-heart-rate averages, not daily exact RHR.
- Because the screenshot values are approximate and graph-derived, they were not merged into `race_context_dataset.csv` or the main statistical findings.
- Some screenshot ranges had no explicit year in the visible title. Those were assigned using the surrounding Garmin sequence and the current visible year context; this is adequate for coverage auditing but remains manual/secondary evidence.

## Images Used

- HRV screenshots with digitized graph points: 50
- RHR screenshots with digitized graph points: 5
- Images not digitized or not usable for graph extraction: 3
- Not digitized: IMG_6414.PNG, IMG_6421.PNG, IMG_6423.PNG

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
| 7 days | 25 | 24 |
| 14 days | 25 | 25 |
| 28 days | 25 | 25 |
| 56 days | 25 | 25 |

## Per-Race Combined Coverage

| Date | Event | HRV export 28d | HRV screenshot 28d | HRV combined 28d | RHR export 28d | RHR screenshot 28d | RHR combined 28d |
|---|---|---:|---:|---:|---:|---:|---:|
| 2023-04-01 | 3000 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2023-05-01 | 3000 metri | 0 | 27 | 27 | 0 | 4 | 4 |
| 2023-05-13 | 1500 metri | 0 | 27 | 27 | 0 | 4 | 4 |
| 2023-05-27 | 1500 metri | 0 | 27 | 27 | 0 | 4 | 4 |
| 2023-05-28 | 5000 metri | 0 | 27 | 27 | 0 | 4 | 4 |
| 2023-06-13 | 2000 siepi H84 | 0 | 27 | 27 | 0 | 3 | 3 |
| 2023-09-09 | 1500 metri | 0 | 27 | 27 | 0 | 4 | 4 |
| 2023-09-10 | 3000 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2024-01-27 | 1500 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2024-04-14 | Corsa 30' Allievi | 0 | 27 | 27 | 0 | 4 | 4 |
| 2024-06-28 | 3000 metri | 0 | 27 | 27 | 0 | 3 | 3 |
| 2024-07-27 | 5000 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2024-08-03 | 3000 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2024-09-08 | 5000 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2024-09-15 | corsa km 5 strada | 0 | 28 | 28 | 0 | 4 | 4 |
| 2024-10-06 | Corsa strada Km 10 | 0 | 28 | 28 | 0 | 4 | 4 |
| 2025-01-18 | 3000 metri | 0 | 27 | 27 | 0 | 4 | 4 |
| 2025-02-09 | 3000 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2025-05-10 | 1500 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2025-05-24 | 1500 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2025-06-29 | 5000 metri | 0 | 28 | 28 | 0 | 3 | 3 |
| 2025-07-23 | 1500 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2025-08-23 | 800 metri | 0 | 26 | 26 | 0 | 4 | 4 |
| 2025-09-06 | 1500 metri | 0 | 27 | 27 | 0 | 4 | 4 |
| 2025-09-07 | 5000 metri | 0 | 28 | 28 | 0 | 4 | 4 |
| 2025-09-28 | 5000 metri | 10 | 28 | 28 | 10 | 4 | 12 |
| 2026-05-01 | 3000 metri | 27 | 28 | 28 | 27 | 4 | 27 |
| 2026-05-17 | 5000 metri | 27 | 28 | 28 | 27 | 4 | 27 |
| 2026-05-30 | 5000 metri | 27 | 28 | 28 | 27 | 3 | 27 |

## Mismatch Check

Overlap mismatches are defined conservatively as screenshot estimate minus export value exceeding 3 ms for HRV or 4 bpm for RHR. These thresholds are not validation thresholds for scientific precision; they are a practical screen for obvious digitization disagreement.

HRV mismatch examples:

- 2025-09-18: export 65.0 ms, screenshot 71.8 ms, diff 6.8.
- 2025-09-19: export 67.0 ms, screenshot 70.8 ms, diff 3.8.
- 2025-09-20: export 75.0 ms, screenshot 70.8 ms, diff -4.2.
- 2025-09-23: export 64.0 ms, screenshot 67.8 ms, diff 3.8.
- 2025-09-25: export 61.0 ms, screenshot 67.8 ms, diff 6.8.
- 2025-09-26: export 62.0 ms, screenshot 66.9 ms, diff 4.9.
- 2025-09-29: export 59.0 ms, screenshot 62.9 ms, diff 3.9.
- 2025-09-30: export 53.0 ms, screenshot 61.9 ms, diff 8.9.
- 2025-10-01: export 56.0 ms, screenshot 59.9 ms, diff 3.9.
- 2025-10-03: export 51.0 ms, screenshot 57.9 ms, diff 6.9.
- 2025-10-05: export 65.0 ms, screenshot 56.9 ms, diff -8.1.
- 2025-10-06: export 61.0 ms, screenshot 56.9 ms, diff -4.1.
- 2025-10-07: export 69.0 ms, screenshot 59.9 ms, diff -9.1.
- 2025-10-08: export 65.0 ms, screenshot 60.9 ms, diff -4.1.
- 2025-10-09: export 72.0 ms, screenshot 62.9 ms, diff -9.1.

RHR mismatch examples:

- 2025-09-19: export 53.0 bpm, screenshot 45.4 bpm, diff -7.6.
- 2025-09-26: export 52.0 bpm, screenshot 47.1 bpm, diff -4.9.
- 2025-10-03: export 57.0 bpm, screenshot 47.7 bpm, diff -9.3.
- 2025-10-10: export 56.0 bpm, screenshot 47.1 bpm, diff -8.9.
- 2025-10-17: export 51.0 bpm, screenshot 46.0 bpm, diff -5.0.
- 2025-10-24: export 55.0 bpm, screenshot 46.8 bpm, diff -8.2.
- 2025-10-31: export 53.0 bpm, screenshot 47.1 bpm, diff -5.9.
- 2025-11-07: export 55.0 bpm, screenshot 48.0 bpm, diff -7.0.
- 2025-11-14: export 57.0 bpm, screenshot 49.1 bpm, diff -7.9.
- 2025-11-21: export 57.0 bpm, screenshot 49.4 bpm, diff -7.6.
- 2025-11-28: export 60.0 bpm, screenshot 49.1 bpm, diff -10.9.
- 2025-12-05: export 55.0 bpm, screenshot 49.7 bpm, diff -5.3.
- 2025-12-12: export 58.0 bpm, screenshot 49.4 bpm, diff -8.6.
- 2025-12-19: export 55.0 bpm, screenshot 48.6 bpm, diff -6.4.
- 2025-12-26: export 53.0 bpm, screenshot 47.4 bpm, diff -5.6.

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
