# AI Methodology

This project uses AI as an analytical assistant, not as an automatic performance predictor.

## What AI Helped With

- Organizing the Garmin export into a research folder structure.
- Inspecting file categories and identifying likely sources for activities, sleep, HRV, heart-rate proxy, VO2max, training status, acute load, race predictions, and personal records.
- Writing reusable Python scripts to create aggregate, privacy-safe datasets.
- Designing simple exploratory figures and a notebook structure.
- Drafting an exploratory scientific paper and maturita-friendly summary.
- Framing cautious interpretations and limitations.

## What AI Did Not Decide Alone

- AI did not certify official race results.
- AI did not diagnose injuries or health status.
- AI did not decide that a variable caused a performance change.
- AI did not build a predictive model claiming that future performance can be forecast.
- AI did not validate Garmin measurements against laboratory equipment.

## Manual Verification Required

The following should be checked manually before presenting the project as final:

- Official race dates, distances, times, venues, and result links.
- Whether each race was tactical, paced evenly, affected by weather, or affected by illness/injury.
- Whether Garmin activity labels match real race contexts.
- Whether the heart-rate proxy used from Garmin health status is acceptable for the intended interpretation.
- Any OptiBioFlow claims that depend on product capabilities or future multi-athlete expansion.

## Risks And Controls

| Risk | Control used in this project |
|---|---|
| Hallucinated facts | The draft uses only generated CSVs, known Garmin summaries, and user-provided official results. Unknown fields are left blank. |
| Overinterpretation | The paper uses exploratory language: association, context, hypothesis generation, and single-athlete case study. |
| Small sample size | The first dataset contains only three high-confidence official race rows, so correlations are explicitly non-inferential. |
| Privacy leakage | Derived outputs omit coordinates, activity IDs, device IDs, raw traces, and private account/social files. |
| Wearable measurement bias | The paper states that Garmin values are consumer wearable estimates, not laboratory-grade measurements. |

## Appropriate AI Claim

The appropriate claim is:

> AI helped organize and interpret wearable-derived data for an exploratory single-athlete case study.

The inappropriate claim is:

> AI predicts endurance performance.

The current dataset does not support that stronger claim.
