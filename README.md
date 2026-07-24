# Morocco Dirham Float: Scenario Explorer

**Interactive risk assessment for Morocco's 2026 currency float using historical peer trajectories.**

## Executive Summary

Morocco plans to float the dirham in 2026. Using pre-float macroeconomic trajectories from six historical currency floats, this project clusters peers by trajectory direction and explores scenario-based outcomes.

**Key Insight:** Morocco's pre-float path clusters with European success cases (Poland, Georgia) rather than African crisis cases (Egypt, Ghana, Nigeria).

**Base Prediction:** 56.5% probability of successful float classification.  
**Uncertainty:** Bootstrap 90% CI: 30.2% – 78.0%.

## Methodology

1. **Data Engineering** — World Bank macro data (2010–2024), 6 countries, 4 indicators
2. **Feature Engineering** — Theil-Sen trend slopes over 3-year pre-float window
3. **Clustering** — Ward hierarchical clustering on standardized means + trends
4. **Classification** — Random Forest (n=5 peers, 8 features)
5. **Uncertainty** — Bootstrap resampling (1,000 iterations)
6. **Scenarios** — Peer-derived path analysis

## Scenario Results

| Scenario | P(Success) | Risk |
|----------|-----------|------|
| Base (Morocco) | 56.5% | Medium |
| Poland Path | 75.8% | High |
| Egypt Path | 16.8% | Low |
| Ghana Path | 5.8% | Low |
| Nigeria Path | 2.5% | Low |

## Limitations

- Small sample (n=6) limits inference
- 3-year pre-float window may miss structural breaks
- Poland debt imputed; Nigeria exchange rate uses official rate
- No causal inference — descriptive pattern matching only

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
