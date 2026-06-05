# Statistical Findings

## Methods

The primary dataset is `data/race_context_dataset.csv`, rebuilt from official FIDAL race results for 2023-2026 and matched to same-day Garmin running activities. The analysis includes 29 official races.

The outcome variable is `performance_score = -relative_performance_pct`. This makes interpretation easier: higher `performance_score` means a race was closer to the athlete's best official result within the same FIDAL event. Correlations are therefore interpreted as:

- positive correlation: higher variable values are associated with better event-relative performance;
- negative correlation: higher variable values are associated with worse event-relative performance.

For each requested Garmin-derived variable, the script calculated Pearson correlation, Spearman correlation, approximate two-sided p-values, and Fisher z 95% confidence intervals when possible. Spearman p-values use the standard large-sample t approximation on ranked data. HRV estimates are sparse and should be interpreted as descriptive only.

Best vs worst quartile comparisons use the best 7 and worst 7 races by event-relative performance.

## Dataset Notes

- Official race rows: 29
- Garmin same-day race matches: 29
- Garmin missing race matches: 0
- Suspicious Garmin match flags: 2
- 7-day HRV available for 4 races only.
- Repeated-event sensitivity rows: 24 races from events with at least 3 imported results.

## Correlation Results

| Variable | n | Pearson r | p | CI low | CI high | Spearman rho | p | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Run km 56d | 29 | 0.633 | 0.0002 | 0.347 | 0.8113 | 0.5912 | 0.0007 | Statistically notable in this dataset; not causal. |
| Run km 28d | 29 | 0.6296 | 0.0003 | 0.342 | 0.8093 | 0.5536 | 0.0018 | Statistically notable in this dataset; not causal. |
| Sleep avg 28d | 29 | 0.5796 | 0.001 | 0.2706 | 0.7804 | 0.4188 | 0.0237 | Statistically notable in this dataset; not causal. |
| Run km 14d | 29 | 0.5045 | 0.0053 | 0.1693 | 0.7351 | 0.401 | 0.0311 | Statistically notable in this dataset; not causal. |
| Sleep avg 14d | 29 | 0.4034 | 0.03 | 0.0433 | 0.6707 | 0.3251 | 0.0853 | Statistically notable in this dataset; not causal. |
| VO2max nearest | 29 | 0.3782 | 0.0431 | 0.0136 | 0.6541 | 0.3854 | 0.039 | Statistically notable in this dataset; not causal. |
| HRV avg 14d | 4 | -0.3594 | 0.6406 | -0.9815 | 0.9192 | 0.2 | 0.8 | Very sparse; treat as descriptive only. |
| HRV avg 7d | 4 | -0.2921 | 0.7079 | -0.9785 | 0.9301 | 0.0 | 1.0 | Very sparse; treat as descriptive only. |
| HRV avg 28d | 4 | -0.2908 | 0.7092 | -0.9784 | 0.9303 | -0.6 | 0.4 | Very sparse; treat as descriptive only. |
| Acute load nearest | 29 | -0.2159 | 0.2607 | -0.5397 | 0.1636 | -0.3007 | 0.113 | Little linear signal in this dataset. |
| RHR proxy 7d | 4 | 0.1631 | 0.8369 | -0.9463 | 0.9718 | 0.6 | 0.4 | Very sparse; treat as descriptive only. |
| Run km 7d | 29 | 0.1579 | 0.4132 | -0.2214 | 0.4957 | 0.0834 | 0.6671 | Little linear signal in this dataset. |
| Sleep avg 7d | 29 | 0.1348 | 0.4857 | -0.2438 | 0.4777 | 0.1825 | 0.3433 | Little linear signal in this dataset. |
| RHR proxy 28d | 4 | -0.1088 | 0.8912 | -0.9686 | 0.9518 | 0.0 | 1.0 | Very sparse; treat as descriptive only. |
| RHR proxy 14d | 4 | 0.0569 | 0.9431 | -0.9565 | 0.9652 | 0.6 | 0.4 | Very sparse; treat as descriptive only. |

## Strongest Positive Associations

| Variable | n | Pearson r | p | Spearman | Evidence |
| --- | --- | --- | --- | --- | --- |
| Run km 56d | 29 | 0.633 | 0.0002 | 0.5912 | Statistically notable in this dataset; not causal. |
| Run km 28d | 29 | 0.6296 | 0.0003 | 0.5536 | Statistically notable in this dataset; not causal. |
| Sleep avg 28d | 29 | 0.5796 | 0.001 | 0.4188 | Statistically notable in this dataset; not causal. |
| Run km 14d | 29 | 0.5045 | 0.0053 | 0.401 | Statistically notable in this dataset; not causal. |
| Sleep avg 14d | 29 | 0.4034 | 0.03 | 0.3251 | Statistically notable in this dataset; not causal. |

## Strongest Negative Associations

| Variable | n | Pearson r | p | Spearman | Evidence |
| --- | --- | --- | --- | --- | --- |
| HRV avg 14d | 4 | -0.3594 | 0.6406 | 0.2 | Very sparse; treat as descriptive only. |
| HRV avg 7d | 4 | -0.2921 | 0.7079 | 0.0 | Very sparse; treat as descriptive only. |
| HRV avg 28d | 4 | -0.2908 | 0.7092 | -0.6 | Very sparse; treat as descriptive only. |
| Acute load nearest | 29 | -0.2159 | 0.2607 | -0.3007 | Little linear signal in this dataset. |
| RHR proxy 28d | 4 | -0.1088 | 0.8912 | 0.0 | Very sparse; treat as descriptive only. |

## Variables With Little Explanatory Value

| Variable | n | Pearson r | p | Spearman |
| --- | --- | --- | --- | --- |
| Run km 7d | 29 | 0.1579 | 0.4132 | 0.0834 |
| Sleep avg 7d | 29 | 0.1348 | 0.4857 | 0.1825 |

## Best 25% vs Worst 25%

| Variable | Best n | Worst n | Best mean | Worst mean | Best - worst | Std diff | Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Run km 7d | 7 | 7 | 54.016 | 45.117 | 8.899 | 0.7279 | Best group higher. |
| Run km 14d | 7 | 7 | 114.414 | 87.494 | 26.92 | 1.696 | Best group higher. |
| Run km 28d | 7 | 7 | 243.764 | 164.64 | 79.124 | 2.8121 | Best group higher. |
| Run km 56d | 7 | 7 | 480.224 | 302.116 | 178.109 | 2.4475 | Best group higher. |
| Sleep avg 7d | 7 | 7 | 8.104 | 7.894 | 0.21 | 0.3252 | Best group higher. |
| Sleep avg 14d | 7 | 7 | 8.129 | 7.771 | 0.357 | 0.9292 | Best group higher. |
| Sleep avg 28d | 7 | 7 | 8.12 | 7.66 | 0.46 | 2.1128 | Best group higher. |
| HRV avg 7d | 1 | 0 | 61.86 |  |  |  | Not enough data. |
| HRV avg 14d | 1 | 0 | 61.69 |  |  |  | Not enough data. |
| HRV avg 28d | 1 | 0 | 61.41 |  |  |  | Not enough data. |
| RHR proxy 7d | 1 | 0 | 52.86 |  |  |  | Not enough data. |
| RHR proxy 14d | 1 | 0 | 52.77 |  |  |  | Not enough data. |
| RHR proxy 28d | 1 | 0 | 52.67 |  |  |  | Not enough data. |
| VO2max nearest | 7 | 7 | 67.857 | 66.571 | 1.286 | 1.1668 | Best group higher. |
| Acute load nearest | 7 | 7 | 721.857 | 803.0 | -81.143 | -0.493 | Best group lower. |

## Sensitivity Check: Repeated Events Only

The main dataset includes one-off events such as 800m, 5 km road, 10 km road, 30-minute run, and steeplechase. Those rows can have `relative_performance_pct = 0` because there is only one official result for that event. As a sensitivity check, the script repeated the correlation analysis on events with at least 3 official rows: 1500m, 3000m, and 5000m.

| Variable | n | Pearson r | p | CI low | CI high | Spearman rho | p | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sleep avg 28d | 24 | 0.7064 | 0.0001 | 0.4237 | 0.8637 | 0.5529 | 0.0051 | Statistically notable in this dataset; not causal. |
| Run km 56d | 24 | 0.6198 | 0.0012 | 0.2885 | 0.8185 | 0.5771 | 0.0031 | Statistically notable in this dataset; not causal. |
| Run km 28d | 24 | 0.6083 | 0.0016 | 0.2715 | 0.8123 | 0.5132 | 0.0103 | Statistically notable in this dataset; not causal. |
| Run km 14d | 24 | 0.559 | 0.0045 | 0.2008 | 0.7853 | 0.4161 | 0.0431 | Statistically notable in this dataset; not causal. |
| Sleep avg 14d | 24 | 0.5259 | 0.0083 | 0.1554 | 0.7666 | 0.4603 | 0.0236 | Statistically notable in this dataset; not causal. |
| VO2max nearest | 24 | 0.4745 | 0.0191 | 0.088 | 0.7369 | 0.5794 | 0.003 | Statistically notable in this dataset; not causal. |
| HRV avg 14d | 4 | -0.3594 | 0.6406 | -0.9815 | 0.9192 | 0.2 | 0.8 | Very sparse; treat as descriptive only. |
| HRV avg 7d | 4 | -0.2921 | 0.7079 | -0.9785 | 0.9301 | 0.0 | 1.0 | Very sparse; treat as descriptive only. |

## Ranked Answer: What Appears To Matter Most?

This ranking combines absolute Pearson and Spearman signal strength, then down-weights variables with sparse coverage. It is a descriptive ranking, not a causal model.

| Rank | Variable | Signal | Raw corr strength | Coverage weight | Pearson | Spearman | n | Best - worst | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Run km 56d | 0.6121 | 0.6121 | 1.0 | 0.633 | 0.5912 | 29 | 178.109 | moderate |
| 2 | Run km 28d | 0.5916 | 0.5916 | 1.0 | 0.6296 | 0.5536 | 29 | 79.124 | moderate |
| 3 | Sleep avg 28d | 0.4992 | 0.4992 | 1.0 | 0.5796 | 0.4188 | 29 | 0.46 | moderate |
| 4 | Run km 14d | 0.4527 | 0.4527 | 1.0 | 0.5045 | 0.401 | 29 | 26.92 | moderate |
| 5 | VO2max nearest | 0.3818 | 0.3818 | 1.0 | 0.3782 | 0.3854 | 29 | 1.286 | moderate |
| 6 | Sleep avg 14d | 0.3642 | 0.3642 | 1.0 | 0.4034 | 0.3251 | 29 | 0.357 | moderate |
| 7 | Acute load nearest | 0.2583 | 0.2583 | 1.0 | -0.2159 | -0.3007 | 29 | -81.143 | low |
| 8 | Sleep avg 7d | 0.1587 | 0.1587 | 1.0 | 0.1348 | 0.1825 | 29 | 0.21 | low |
| 9 | Run km 7d | 0.1207 | 0.1207 | 1.0 | 0.1579 | 0.0834 | 29 | 8.899 | low |
| 10 | HRV avg 28d | 0.0614 | 0.4454 | 0.1379 | -0.2908 | -0.6 | 4 |  | very low |
| 11 | RHR proxy 7d | 0.0526 | 0.3816 | 0.1379 | 0.1631 | 0.6 | 4 |  | very low |
| 12 | RHR proxy 14d | 0.0453 | 0.3284 | 0.1379 | 0.0569 | 0.6 | 4 |  | very low |
| 13 | HRV avg 14d | 0.0386 | 0.2797 | 0.1379 | -0.3594 | 0.2 | 4 |  | very low |
| 14 | HRV avg 7d | 0.0201 | 0.1461 | 0.1379 | -0.2921 | 0.0 | 4 |  | very low |
| 15 | RHR proxy 28d | 0.0075 | 0.0544 | 0.1379 | -0.1088 | 0.0 | 4 |  | very low |

## Interpretation

The strongest complete-data signals are the longer running-volume windows, especially 56-day and 28-day running volume. In this athlete's official 2023-2026 FIDAL race dataset, higher pre-race running volume is generally associated with better event-relative performance. This remains visible in the repeated-event sensitivity check, so it is not only an artifact of one-off event rows. This is consistent with the idea that sustained aerobic training volume matters for middle-distance/endurance development.

VO2max also shows a positive descriptive relationship with better event-relative performance. Because Garmin VO2max is model-derived and partly influenced by recent running performance, it should be interpreted as a fitness-context indicator rather than an independent cause.

Acute load shows weaker explanatory value than longer running-volume windows. This suggests that the short-term load number alone is less informative than the accumulated training context, at least in this dataset.

Sleep shows a time-window-dependent signal. The 7-day sleep average has little explanatory value, but 14-day and especially 28-day sleep averages show positive associations with better event-relative performance. In the repeated-event sensitivity check, 28-day sleep is the strongest single association. This should still be interpreted cautiously: sleep may reflect broader recovery, consistency, season phase, school/life load, illness, or taper context rather than acting as a simple independent cause.

HRV and RHR proxy are limited by coverage in the race-context table. They are available only for a few later races, making p-values and confidence intervals unreliable. RHR proxy also remains a wearable-derived proxy, not a controlled physiological measurement.

## Limitations

- Single-athlete observational case study; no causal inference.
- Mixed race events; `relative_performance_pct` normalizes within event but cannot remove all event-specific differences.
- Unique-event rows such as 800m, 5 km road, 10 km road, 30-minute run, and steeplechase have limited within-event comparison.
- HRV coverage is sparse.
- Garmin VO2max, acute load, HRV, sleep, and RHR proxy are consumer wearable estimates.
- Race tactics, weather, illness, injury, competition level, and taper intent are not fully controlled.
- P-values are exploratory and not corrected for multiple comparisons.

## Figures

- `figures/stat_correlation_rankings.png`
- `figures/stat_best_worst_quartile_differences.png`
- `figures/stat_top_relationships_scatter.png`
- `figures/stat_best_worst_races.png`
