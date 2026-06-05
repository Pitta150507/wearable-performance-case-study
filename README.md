# Training Volume, Sleep and Endurance Performance: A Longitudinal Analysis of 29 Official Races in a Competitive Distance Runner

A Four-Year Wearable-Based Case Study (2023-2026)

Author: Andrea Bertoldo, Independent Student Researcher, Italy

## Overview

This repository contains a reproducible single-athlete observational case study linking official FIDAL race results with Garmin Connect training and recovery data. The primary dataset contains 29 official FIDAL races from 2023-2026, matched to same-day Garmin activities.

The paper is version 1.0 and is scientifically complete for public release. The analysis is descriptive and does not make causal claims.

## Data Summary

- Garmin Connect export: 2022-07-21 to 2026-06-03
- Activities: 3,166
- Runs: 2,092
- Running distance: 9,052.8 km
- Sleep records: 1,403
- Exact HRV records: 256
- Official FIDAL races: 29
- Garmin race matches: 29

## Key Findings

- 56-day running volume: r = 0.633, p = 0.0002
- 28-day running volume: r = 0.630, p = 0.0003
- 28-day sleep average: r = 0.580, p = 0.001
- 14-day running volume: r = 0.505, p = 0.0053
- VO2max nearest: r = 0.378, p = 0.0431
- 14-day sleep average: r = 0.403, p = 0.030

## Methods

Official race results were treated as the ground truth and imported from the athlete's FIDAL profile. Garmin data were used to compute pre-race training volume, sleep, HRV/RHR coverage, VO2max, and acute-load context. The outcome variable was event-relative official race performance.

## Limitations

- Single-athlete case study.
- Exploratory observational design.
- No causal inference.
- Mixed race events.
- Consumer wearable estimates are not laboratory measures.
- Exact HRV/RHR export coverage is sparse.
- Screenshot-derived HRV/RHR graph estimates are supplementary only and excluded from the primary statistical analysis.

## Reproducibility

Run the scripts in `scripts/` from this directory. Key outputs are in `data/`, `figures/`, `tables/`, `docs/`, `paper/`, and `publication/`.

Recommended order:

1. `scripts/build_activity_summary.py`
2. `scripts/build_health_summary.py`
3. `scripts/build_official_race_list.py`
4. `scripts/build_race_context_dataset.py`
5. `scripts/statistical_analysis.py`
6. `scripts/audit_hrv_rhr_coverage.py`
7. `scripts/digitize_screenshot_graphs.py`
8. `scripts/prepare_public_release.py`

## Manuscript

- `paper/final_manuscript.md`
- `paper/final_manuscript.docx`
- `paper/final_manuscript.pdf`

## Release

- Repository: https://github.com/Pitta150507/wearable-performance-case-study
- GitHub Release v1.0: https://github.com/Pitta150507/wearable-performance-case-study/releases/tag/v1.0
- Curated upload archive: `publication/wearable-performance-case-study-v1.0-release.zip`

## Citation

Please cite this repository using `CITATION.cff`.

Suggested citation:

Bertoldo, A. (2026). *Training Volume, Sleep and Endurance Performance: A Longitudinal Analysis of 29 Official Races in a Competitive Distance Runner* (Version 1.0). Zenodo/OSF/GitHub release package.
