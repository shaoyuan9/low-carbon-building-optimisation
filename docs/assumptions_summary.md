# Assumptions Summary

This file summarizes the key assumptions used in the Version 1 low-carbon building decision-support model. It is adapted from the Variables & Sources Tracker in the local project handbook, excluding next actions and working notes.

## Project Assumptions

| ID | Assumption | Value | Source | Confidence | Status |
| --- | --- | --- | --- | --- | --- |
| A-001 | Target emissions reduction | 0.20 | Project objective | High | Confirmed |
| A-002 | Project lifetime | 25 years | [EMA solar lifetime][ema-solar-lifetime] | High | Confirmed |
| A-003 | Discount rate | 0.05 | Engineering estimate | Medium | Preliminary |

Used in: `configs/base_case.yaml`, `cost_model.py`, `emissions_model.py`

Validation focus: target logic checks, PV asset lifetime benchmark, and future discount-rate sensitivity testing.

## Building Assumptions

| ID | Assumption | Value | Source | Confidence | Status |
| --- | --- | --- | --- | --- | --- |
| A-004 | Annual electricity demand | 2,400,000 kWh/year | [EMA energy statistics][ema-energy-ch3], [NUS literature][nus-energy], SLEB disclosure data | Medium | Confirmed |
| A-005 | Available rooftop area | 5,000 m2 | Representative building case | Medium | Preliminary |

Used in: `configs/base_case.yaml`, `load_model.py`, `solar_pv_model.py`

Validation focus: replace annual demand with actual or synthetic hourly load in Version 2; check rooftop area against PV sizing and roof-layout assumptions.

## Grid Assumptions

| ID | Assumption | Value | Source | Confidence | Status |
| --- | --- | --- | --- | --- | --- |
| A-006 | Electricity price | SGD 0.30/kWh | [SP Group tariff information][sp-tariff] | High | Confirmed |
| A-007 | Grid emission factor | 0.40 kgCO2/kWh | [EMA grid emission factor][ema-energy-ch2] | High | Confirmed |
| A-008 | Electricity price escalation rate | 0.00/year | Scenario assumption | Medium | Preliminary |

Used in: `configs/base_case.yaml`, `cost_model.py`, `emissions_model.py`

Validation focus: compare grid emission factor with official Singapore publications and test price escalation scenarios in later versions.

## Solar PV Assumptions

| ID | Assumption | Value | Source | Confidence | Status |
| --- | --- | --- | --- | --- | --- |
| A-009 | PV technology name | `representative_commercial_rooftop_pv` | Version 1 representative technology | Medium | Preliminary |
| A-010 | PV CAPEX | SGD 1,200/kWp | [EMA solar PV installation guidance][ema-solar-guidance] | Medium | Confirmed |
| A-011 | PV OPEX | 1% of CAPEX/year | [EMA solar PV installation guidance][ema-solar-guidance] | Medium | Confirmed |
| A-012 | Annual PV yield | 1,200 kWh/kWp/year | [SERIS Solar Economics Handbook][seris-handbook] | Medium | Preliminary |
| A-013 | PV degradation rate | 0.005/year | [Solar degradation reference][solar-degradation] | Medium | Preliminary |
| A-014 | Area requirement | 5 m2/kWp | [Solar area reference][solar-area] | Medium | Preliminary |
| A-015 | PV OPEX escalation rate | 0.00/year | Scenario assumption | Medium | Preliminary |

Used in: `configs/base_case.yaml`, `solar_pv_model.py`, `cost_model.py`

Validation focus: benchmark PV CAPEX, OPEX, yield, degradation, and area requirement against Singapore market references and future technology-specific datasets.

## Renewable Purchase Assumptions

| ID | Assumption | Value | Source | Confidence | Status |
| --- | --- | --- | --- | --- | --- |
| A-016 | Renewable purchase premium | SGD 0.03/kWh | Placeholder for green tariff, REC, or contract reference | Low | Needs source |
| A-017 | Renewable electricity emission factor | 0 kgCO2/kWh | Market-based accounting simplification | Medium | Needs validation |

Used in: `configs/base_case.yaml`, `cost_model.py`, `emissions_model.py`

Validation focus: replace placeholder premium with market evidence and document the accounting boundary for renewable electricity purchases.

## Baseline Analysis And Scope Assumptions

| ID | Assumption | Value | Source | Confidence | Status |
| --- | --- | --- | --- | --- | --- |
| A-018 | Hybrid PV share of target | 0.50 | Modelling design choice | Medium | Preliminary |
| A-019 | Renewable purchase accounting | Premium only | Version 1 accounting rule | High | Confirmed |
| A-020 | Battery not included in Version 1 | Excluded | [Version roadmap](version_history.md) | High | Confirmed |
| A-021 | Hourly solar variability not included in Version 1 | Excluded | [Version roadmap](version_history.md) | High | Confirmed |
| A-022 | Policy scenarios not included in Version 1 | Excluded | [Version roadmap](version_history.md) | High | Confirmed |

Used in: `baseline_analysis.py`, `cost_model.py`, `emissions_model.py`, `docs/version_history.md`

Validation focus: test alternative hybrid PV shares in sensitivity analysis and extend the model in later versions to include hourly realism, batteries, and policy scenarios.

[ema-solar-lifetime]: https://www.ema.gov.sg/resources/faqs/solar/solar-installation-guide/how-long-will-a-solar-pv-system-last
[ema-energy-ch3]: https://www.ema.gov.sg/resources/singapore-energy-statistics/chapter3
[nus-energy]: https://nus.edu.sg/newshub/news/2025/2025-05/2025-05-08/ENERGY-bt-8may-p11.pdf
[sp-tariff]: https://www.spgroup.com.sg/our-services/utilities/tariff-information
[ema-energy-ch2]: https://www.ema.gov.sg/resources/singapore-energy-statistics/chapter2
[ema-solar-guidance]: https://www.ema.gov.sg/consumer-information/solar/evaluating-potential-for-solar-pv-installation
[seris-handbook]: https://www.seris.nus.edu.sg/wp-content/uploads/2023/08/SERIS-Solar-Economics-Handbook_December-2019.pdf
[solar-degradation]: https://www.sunollo.com/blog/solar-panel-degradation-singapore-guide-2026
[solar-area]: https://www.eigen.energy/articles/homes-solar-power-needs-singapore
