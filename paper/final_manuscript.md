# Training Volume, Sleep and Endurance Performance: A Longitudinal Analysis of 29 Official Races in a Competitive Distance Runner

## A Four-Year Wearable-Based Case Study (2023-2026)

**Author:** Andrea Bertoldo  
**Affiliation:** Independent Student Researcher, Italy  
**Manuscript version:** 1.0  
**Date:** 2026-06-05  

## Abstract

This exploratory single-athlete case study examined whether Garmin-derived training and recovery variables were associated with official endurance-race performance. The primary dataset included 29 official FIDAL race results from 2023-04-01 to 2026-05-30, each matched to a same-day Garmin running activity. Garmin export coverage spanned 2022-07-21 to 2026-06-03 and included 3,166 activities, 2,092 runs, 9,052.8 km of running, 1,403 sleep records, and 256 export-derived HRV records. Performance was normalized within official event type using an event-relative performance score, where higher values indicate better performance relative to the athlete's best official result in the same event. The strongest complete-data associations were observed for 56-day running volume (Pearson r = 0.633, p = 0.0002), 28-day running volume (r = 0.630, p = 0.0003), 28-day sleep average (r = 0.580, p = 0.001), 14-day running volume (r = 0.505, p = 0.0053), VO2max nearest to race day (r = 0.378, p = 0.0431), and 14-day sleep average (r = 0.403, p = 0.030). HRV and resting heart rate were not suitable for primary inference because exact export coverage was limited to four race rows. Screenshot-derived HRV/RHR graph digitizations improved historical coverage as secondary evidence but were excluded from the primary analysis because they were approximate and not equivalent to export-derived daily values. These findings suggest that, in this athlete, longer-term running volume and multi-week sleep consistency contained the clearest wearable-derived signals, but the design is observational and does not support causal claims.

## Keywords

wearable data; endurance running; Garmin; sleep; training volume; FIDAL; single-athlete case study; observational analysis

## Introduction

Wearable devices produce dense longitudinal records of training, sleep, and physiological estimates. For endurance athletes, these records may help describe the training context that precedes competition. However, consumer wearable variables are not controlled laboratory measures, and their relationship with race performance is often difficult to interpret because performance is shaped by event distance, training phase, tactics, weather, injury status, competition level, and recovery.

This project analyzes one competitive distance runner's longitudinal data using official race results as the performance ground truth. Official FIDAL results were treated as the authoritative source for race dates, events, and times. Garmin Connect data were used only to characterize pre-race training and recovery context. The purpose was descriptive: to identify whether any wearable-derived variables showed meaningful association with event-relative official race performance.

The primary research question was: which Garmin-derived variables appear most strongly associated with official endurance-race performance in this athlete across the 2023-2026 competition period?

## Methods

### Study Design

This is an exploratory, observational, single-athlete longitudinal case study. It is not an intervention study and does not support causal inference. All associations are interpreted as descriptive signals within one athlete's historical data.

### Athlete and Data Sources

The athlete was Andrea Bertoldo, an independent student researcher based in Italy. The Garmin Connect export covered 2022-07-21 to 2026-06-03. The derived activity dataset contained 3,166 activities, including 2,092 running activities and 9,052.8 km of running. Sleep coverage included 1,403 sleep records. HRV exact export coverage included 256 records.

Official race results were imported from the athlete's FIDAL profile and manually validated. The final primary race dataset included 29 official FIDAL race rows from 2023-2026. Each official race was matched to a same-day Garmin running activity; 29 of 29 rows had Garmin matches. Two matches were flagged as potentially suspicious for manual review, but all official race rows were retained because FIDAL remained the race-performance ground truth.

### Race Inclusion Criteria

The analysis focused on middle-distance and endurance-relevant official events from 2023-2026, including 1500 m, 3000 m, 5000 m, road 5 km, road 10 km, 30-minute run, and steeplechase where useful for history. Childhood and non-endurance events were excluded from the primary race-context dataset.

### Outcome Variable

Race performance was modeled as an event-relative performance score. For each official event type, the athlete's best official time was used as the within-event reference. The analysis used `performance_score = -relative_performance_pct`, so higher scores indicate a race closer to the athlete's best official result within the same event. This normalization reduces, but does not eliminate, differences across event types.

### Predictor Variables

The primary tested variables were:

- running volume in the previous 7, 14, 28, and 56 days;
- sleep average in the previous 7, 14, and 28 days;
- HRV average in the previous 7, 14, and 28 days;
- resting heart rate proxy in the previous 7, 14, and 28 days;
- Garmin VO2max nearest to race day;
- Garmin acute load nearest to race day.

### HRV and Resting Heart Rate Handling

Exact Garmin export-derived HRV and RHR-proxy records were available only from 2025-09-18 to 2026-06-04, yielding preceding-28-day coverage for only four race rows. A later screenshot integration audit digitized Garmin graph screenshots as secondary/manual evidence. Those screenshot-derived HRV/RHR values were approximate graph extractions, not exact export records. They were therefore excluded from the primary statistical analysis.

### Statistical Analysis

Pearson and Spearman correlations were computed between each predictor and event-relative performance score. Approximate two-sided p-values and Fisher z confidence intervals were reported when possible. Best-quartile and worst-quartile race groups were compared using the best seven and worst seven official races by event-relative performance. P-values were exploratory and not corrected for multiple comparisons.

## Results

### Dataset Summary

The final dataset contained 29 official FIDAL races and 29 Garmin same-day activity matches. Garmin export coverage included 3,166 activities, 2,092 runs, 9,052.8 km of running, 1,403 sleep records, and 256 exact HRV records.

### Primary Association Results

The strongest complete-data associations were observed for longer running-volume windows and multi-week sleep averages. The leading Pearson correlations were:

| Variable | n | Pearson r | p | 95% CI low | 95% CI high | Spearman rho | p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Run km 56d | 29 | 0.633 | 0.0002 | 0.347 | 0.811 | 0.591 | 0.0007 |
| Run km 28d | 29 | 0.630 | 0.0003 | 0.342 | 0.809 | 0.554 | 0.0018 |
| Sleep avg 28d | 29 | 0.580 | 0.001 | 0.271 | 0.780 | 0.419 | 0.0237 |
| Run km 14d | 29 | 0.505 | 0.0053 | 0.169 | 0.735 | 0.401 | 0.0311 |
| Sleep avg 14d | 29 | 0.403 | 0.030 | 0.043 | 0.671 | 0.325 | 0.0853 |
| VO2max nearest | 29 | 0.378 | 0.0431 | 0.014 | 0.654 | 0.385 | 0.039 |

Table 1 provides the full correlation results in `tables/final_table_01.csv`. Figure 2 summarizes the ranked correlation signals, and Figure 3 shows scatterplots for the strongest complete-data relationships.

### Best Versus Worst Quartile

The best seven races by event-relative performance showed higher running volume across 7-, 14-, 28-, and 56-day windows and higher 14- and 28-day sleep averages than the worst seven races. The largest standardized differences were observed for 28-day running volume, 56-day running volume, and 28-day sleep average.

| Variable | Best mean | Worst mean | Difference | Std diff | Direction |
| --- | --- | --- | --- | --- | --- |
| Run km 14d | 114.414 | 87.494 | 26.920 | 1.696 | Best group higher. |
| Run km 28d | 243.764 | 164.640 | 79.124 | 2.812 | Best group higher. |
| Run km 56d | 480.224 | 302.116 | 178.109 | 2.448 | Best group higher. |
| Sleep avg 28d | 8.120 | 7.660 | 0.460 | 2.113 | Best group higher. |
| VO2max nearest | 67.857 | 66.571 | 1.286 | 1.167 | Best group higher. |
| Acute load nearest | 721.857 | 803.000 | -81.143 | -0.493 | Best group lower. |

The complete comparison is provided in `tables/final_table_02.csv` and Figure 4.

### HRV/RHR Coverage

The exact Garmin export contained 256 HRV records and 256 RHR-proxy records, beginning on 2025-09-18. Only four of the 29 official races had exact HRV/RHR coverage in the preceding 28 days. Screenshot-derived graph digitization improved apparent historical coverage, but these estimates were approximate, often rolling or weekly, and showed substantial mismatch with export values on overlapping dates. They were therefore retained as supplementary evidence only and excluded from the primary analysis.

### Signal Ranking

The descriptive ranking from strongest to weakest complete-data signal was:

1. 56-day running volume
2. 28-day running volume
3. 28-day sleep average
4. 14-day running volume
5. VO2max nearest
6. 14-day sleep average
7. Acute load nearest
8. 7-day sleep average
9. 7-day running volume

HRV and RHR variables were ranked as very low-confidence because only four race rows had exact export coverage.

## Discussion

The clearest signals in this single-athlete dataset were longer-term running-volume windows. The 56-day and 28-day running-volume variables showed similar Pearson correlations with event-relative performance, suggesting that sustained training context was more informative than the final 7 days alone. This is plausible for middle-distance and endurance performance, where chronic aerobic development and accumulated training consistency often matter more than very short-term volume.

Sleep showed a window-dependent pattern. The 7-day sleep average had little explanatory value, whereas 14-day and 28-day averages showed stronger positive associations. In the repeated-event sensitivity analysis documented in the statistical report, 28-day sleep remained a strong signal. This may indicate that multi-week sleep consistency captured broader recovery context better than the immediate pre-race week. It should not be interpreted as proof that increasing sleep alone caused faster performances.

VO2max nearest to race day showed a smaller but positive association. Garmin VO2max is model-derived and partly influenced by recent running performance, so it is best interpreted as a general fitness-context marker rather than an independent explanatory variable.

Acute load was weaker than longer running-volume windows. This suggests that, in this dataset, accumulated running volume contained more performance-relevant information than a short-term load estimate alone. HRV and RHR could not be meaningfully interpreted in the primary statistical analysis because exact export coverage was too sparse.

## Limitations

- This is a single-athlete case study and may not generalize to other runners.
- The design is exploratory and observational; no causal claims are made.
- Race events were mixed. Event-relative normalization reduces but cannot remove all differences between 1500 m, 3000 m, 5000 m, road races, and other events.
- P-values are exploratory and were not corrected for multiple comparisons.
- Garmin-derived sleep, VO2max, acute load, HRV, and RHR-proxy variables are consumer wearable estimates, not controlled laboratory measurements.
- Exact HRV/RHR coverage was limited to four race rows.
- Screenshot-derived HRV/RHR values were approximate graph digitizations and excluded from the primary statistical analysis.
- Race tactics, weather, illness, injury, school/life stress, competition quality, and taper intent were not fully controlled.

## Conclusion

Across 29 official FIDAL races from 2023-2026, the strongest Garmin-derived signals associated with event-relative performance were longer-term running volume and multi-week sleep averages. The leading associations were 56-day running volume (r = 0.633), 28-day running volume (r = 0.630), and 28-day sleep average (r = 0.580). VO2max nearest to race day showed a smaller positive association. HRV and RHR exact export coverage was too sparse for primary inference, and screenshot-derived graph estimates were kept as supplementary evidence only. The results support a cautious descriptive conclusion: in this athlete, sustained training volume and multi-week sleep consistency appear to contain meaningful wearable-derived performance context, but the analysis remains observational and non-causal.

## References

1. Federazione Italiana di Atletica Leggera (FIDAL). Official athlete profile and race results for Andrea Bertoldo. Used as the authoritative source for official race dates, events, and times.
2. Garmin Connect. Personal data export, 2022-07-21 to 2026-06-03. Used for activity, training, sleep, HRV, RHR-proxy, VO2max, and acute-load context.
3. Project source files: `data/race_context_dataset.csv`, `data/stat_correlation_results.csv`, `data/stat_signal_ranking.csv`, `docs/Statistical_Findings.md`, `docs/HRV_RHR_Coverage_Audit.md`, and `docs/HRV_RHR_Screenshot_Integration_Report.md`.

## Appendix

### Appendix A. Reproducibility

The analysis is reproducible from the project scripts and derived CSV files:

1. `scripts/inspect_garmin_export.py`
2. `scripts/build_activity_summary.py`
3. `scripts/build_health_summary.py`
4. `scripts/build_official_race_list.py`
5. `scripts/build_race_context_dataset.py`
6. `scripts/statistical_analysis.py`
7. `scripts/audit_hrv_rhr_coverage.py`
8. `scripts/digitize_screenshot_graphs.py`
9. `scripts/prepare_public_release.py`

### Appendix B. Final Figures

- Figure 1: `figures/final_figure_01.png`
- Figure 2: `figures/final_figure_02.png`
- Figure 3: `figures/final_figure_03.png`
- Figure 4: `figures/final_figure_04.png`
- Figure 5: `figures/final_figure_05.png`

### Appendix C. Final Tables

- Table 1: `tables/final_table_01.csv`
- Table 2: `tables/final_table_02.csv`
- Table 3: `tables/final_table_03.csv`
