# Final Release Audit

Date: 2026-06-05

## Scope

Release package for version 1.0 of:

Training Volume, Sleep and Endurance Performance: A Longitudinal Analysis of 29 Official Races in a Competitive Distance Runner

## Manuscript Consistency

- Title, author, abstract, methods, results, discussion, limitations, conclusion, references, and appendix are present.
- The manuscript explicitly states 29 official FIDAL races.
- Garmin export date range is stated as 2022-07-21 to 2026-06-03.
- HRV/RHR export coverage limitation is stated.
- Screenshot-derived HRV/RHR are described as approximate and excluded from primary analysis.
- The design is described as exploratory and observational.
- No causal claims are made.

## Statistical Value Check

- Run km 56d: expected r=0.633, p=0.0002; observed r=0.633, p=0.0002; PASS
- Run km 28d: expected r=0.630, p=0.0003; observed r=0.630, p=0.0003; PASS
- Sleep avg 28d: expected r=0.580, p=0.001; observed r=0.580, p=0.001; PASS
- Run km 14d: expected r=0.505, p=0.0053; observed r=0.505, p=0.0053; PASS
- VO2max nearest: expected r=0.378, p=0.0431; observed r=0.378, p=0.0431; PASS
- Sleep avg 14d: expected r=0.403, p=0.030; observed r=0.403, p=0.030; PASS

## Figure References

- Figure 1: `figures/final_figure_01.png`
- Figure 2: `figures/final_figure_02.png`
- Figure 3: `figures/final_figure_03.png`
- Figure 4: `figures/final_figure_04.png`
- Figure 5: `figures/final_figure_05.png`

All five final figures exist and are referenced in the manuscript appendix.

## Table References

- Table 1: `tables/final_table_01.csv`
- Table 2: `tables/final_table_02.csv`
- Table 3: `tables/final_table_03.csv`

Captions are stored in `tables/final_table_captions.md`.

## Privacy Compliance

Top-level derived CSV files checked:

- data/daily_training_summary.csv
- data/race_context_dataset.csv
- data/activity_summary.csv
- data/hrv_rhr_combined_coverage_audit.csv
- data/stat_signal_ranking.csv
- data/garmin_export_inventory.csv
- data/fidal_official_results.csv
- data/hrv_graph_digitized.csv
- data/manual_hrv_rhr_from_screenshots.csv
- data/manual_screenshot_inventory.csv
- data/stat_correlation_results_repeated_events.csv
- data/activity_duplicate_check.csv
- data/rhr_graph_digitized.csv
- data/hrv_rhr_race_coverage_audit.csv
- data/stat_correlation_results.csv
- data/daily_health_summary.csv
- data/stat_best_worst_quartile_comparison.csv

Potential sensitive header scan:

- No GPS coordinate, Garmin ID, email, phone, owner, or latitude/longitude columns detected in top-level derived CSV headers.

Notes:

- The public package should exclude raw Garmin export folders and original route files.
- Derived race data include public FIDAL source URLs and public race city names.
- The pseudonymous athlete id `single_athlete_001` is used in the race-context table.
- Manual screenshots should be reviewed by Andrea before public upload if included; the report treats them as supplementary.

## Release Readiness

- Scientific manuscript: ready for public preprint/repository release.
- GitHub repository: published at `https://github.com/Pitta150507/wearable-performance-case-study`.
- GitHub Release v1.0: published at `https://github.com/Pitta150507/wearable-performance-case-study/releases/tag/v1.0`.
- Zenodo package: metadata and checklist prepared.
- OSF package: metadata and checklist prepared.

## Manual Actions Before Publication

1. Review all files in `data/` and confirm no private raw Garmin exports are included.
2. Decide whether `data/manual_screenshots/` should be public or kept private.
3. Add DOI values after Zenodo/OSF publication.
4. Confirm license choice for derived data if different from MIT code/documentation.
