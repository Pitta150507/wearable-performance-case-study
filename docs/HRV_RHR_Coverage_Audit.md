# HRV/RHR Coverage Audit

## Summary

This audit verifies HRV and RHR-proxy coverage directly from `data/daily_health_summary.csv` and compares it to the 29 official FIDAL race rows in `data/race_context_dataset.csv`.

| Check | HRV | RHR proxy |
|---|---:|---:|
| Total rows available | 256 | 256 |
| First date | 2025-09-18 | 2025-09-18 |
| Last date | 2026-06-04 | 2026-06-04 |
| Official races with preceding-28-day coverage | 4 | 4 |

Result: the statistical report statement is correct. HRV/RHR coverage is sparse for race inference because Garmin HRV/RHR-proxy rows begin on 2025-09-18. Only 4 of the 29 official race rows have HRV/RHR data in the preceding 28 days.

## Source-Data Cross-Check

The derived health summary was checked against the raw Garmin `healthStatusData` exports.

| Check | Result |
|---|---:|
| Raw health-status source files | 3 |
| Raw HRV-valued records | 256 |
| Raw HR-valued records used as RHR proxy | 256 |
| Raw HRV date range | 2025-09-18 to 2026-06-04 |
| Raw HR date range | 2025-09-18 to 2026-06-04 |
| Separate raw `RHR` metric present | no |

Raw metric types present:

- HR: 256
- HRV: 256
- RESPIRATION: 256
- SKIN_TEMP_C: 256
- SPO2: 256

Interpretation: the low coverage is not caused by the parser skipping older HRV/RHR rows. The Garmin export contains HRV and HR health-status records only from 2025-09-18 onward, and no separate `RHR` metric is present in these files. The `rhr_*` race-context variables therefore remain a Garmin health-status HR proxy.

## Per-Race Coverage

| Date | Event | Official | Window | HRV days | RHR days | HRV? | RHR? | Missing reason |
|---|---|---:|---|---:|---:|---|---|---|
| 2023-04-01 | 3000 metri | 10:11.12 | 2023-03-04 to 2023-03-31 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2023-05-01 | 3000 metri | 10:21.75 | 2023-04-03 to 2023-04-30 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2023-05-13 | 1500 metri | 4:35.28 | 2023-04-15 to 2023-05-12 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2023-05-27 | 1500 metri | 4:30.99 | 2023-04-29 to 2023-05-26 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2023-05-28 | 5000 metri | 18:13.91 | 2023-04-30 to 2023-05-27 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2023-06-13 | 2000 siepi H84 | 6:52.10 | 2023-05-16 to 2023-06-12 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2023-09-09 | 1500 metri | 4:22.83 | 2023-08-12 to 2023-09-08 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2023-09-10 | 3000 metri | 9:43.52 | 2023-08-13 to 2023-09-09 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2024-01-27 | 1500 metri | 4:30.80 | 2023-12-30 to 2024-01-26 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2024-04-14 | Corsa 30' Allievi | 30:00 | 2024-03-17 to 2024-04-13 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2024-06-28 | 3000 metri | 9:52.80 | 2024-05-31 to 2024-06-27 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2024-07-27 | 5000 metri | 16:50.28 | 2024-06-29 to 2024-07-26 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2024-08-03 | 3000 metri | 9:18.53 | 2024-07-06 to 2024-08-02 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2024-09-08 | 5000 metri | 16:16.13 | 2024-08-11 to 2024-09-07 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2024-09-15 | corsa km 5 strada | 16:31 | 2024-08-18 to 2024-09-14 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2024-10-06 | Corsa strada Km 10 | 34:14 | 2024-09-08 to 2024-10-05 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2025-01-18 | 3000 metri | 9:12.22 | 2024-12-21 to 2025-01-17 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2025-02-09 | 3000 metri | 9:06.25 | 2025-01-12 to 2025-02-08 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2025-05-10 | 1500 metri | 4:25.56 | 2025-04-12 to 2025-05-09 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2025-05-24 | 1500 metri | 4:23.47 | 2025-04-26 to 2025-05-23 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2025-06-29 | 5000 metri | 16:02.66 | 2025-06-01 to 2025-06-28 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2025-07-23 | 1500 metri | 4:10.61 | 2025-06-25 to 2025-07-22 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2025-08-23 | 800 metri | 2:05.66 | 2025-07-26 to 2025-08-22 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2025-09-06 | 1500 metri | 4:15.27 | 2025-08-09 to 2025-09-05 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2025-09-07 | 5000 metri | 15:59.98 | 2025-08-10 to 2025-09-06 | 0 | 0 | no | no | date outside HRV/RHR availability |
| 2025-09-28 | 5000 metri | 15:54.20 | 2025-08-31 to 2025-09-27 | 10 | 10 | yes | yes | covered |
| 2026-05-01 | 3000 metri | 9:11.10 | 2026-04-03 to 2026-04-30 | 27 | 27 | yes | yes | covered |
| 2026-05-17 | 5000 metri | 15:54.63 | 2026-04-19 to 2026-05-16 | 27 | 27 | yes | yes | covered |
| 2026-05-30 | 5000 metri | 15:43.94 | 2026-05-02 to 2026-05-29 | 27 | 27 | yes | yes | covered |

## Covered Races

4 races have HRV/RHR coverage in the preceding 28 days:

- 2025-09-28 5000 metri (15:54.20): HRV days 10, RHR days 10.
- 2026-05-01 3000 metri (9:11.10): HRV days 27, RHR days 27.
- 2026-05-17 5000 metri (15:54.63): HRV days 27, RHR days 27.
- 2026-05-30 5000 metri (15:43.94): HRV days 27, RHR days 27.

## Missing-Coverage Explanation

25 races have no HRV/RHR data in the preceding 28 days.

Reason breakdown:

- covered: 4
- date outside HRV/RHR availability: 25

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
