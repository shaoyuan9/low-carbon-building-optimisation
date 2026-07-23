# A Modular Techno-Economic Optimisation Framework for Low-Carbon Electricity Strategies in Singapore Commercial Buildings

## Objective
Develop a techno-economic decision-support model to identify the least-cost strategy for a Singapore commercial building owner to achieve at least 20% electricity-related emissions reduction.

## Version 1 Scope
This version compares:
1. Grid electricity baseline
2. Renewable electricity purchase
3. Rooftop solar PV
4. Solar PV + renewable electricity purchase

## Key Questions
- What is the baseline emissions level?
- How much emissions reduction is required to reach 20%?
- Can solar PV alone meet the target?
- If not, how much renewable electricity purchase is required?
- Which option has the lowest cost?

## Version 1 Logic Flow
Version 1 uses a configuration-driven workflow to compare four baseline strategies: grid electricity, renewable electricity purchase, rooftop solar PV, and solar PV with renewable electricity purchase.

```text
main.py
    |
    +--> config_loader.py
    |       reads base_case.yaml
    |       returns BaselineAnalysisInput
    |
    +--> run_baseline_analysis()
    |       compares four strategies:
    |       1. Grid baseline
    |       2. Renewable electricity purchase only
    |       3. Solar PV only
    |       4. Solar PV + renewable electricity purchase
    |
    |       each strategy calls:
    |       - load_model.py
    |       - solar_pv_model.py
    |       - emissions_model.py
    |       - cost_model.py
    |
    |       returns:
    |       - list[StrategyResult]
    |
    +--> baseline_results_to_dataframe()
    |       converts StrategyResult outputs into DataFrame
    |
    +--> baseline_results.csv
    |
    +--> plots.py
    |       generates visual comparison charts
    |
    +--> select_recommended_strategy()
            filters strategies where target_met == True
            selects highest npv_sgd
            returns recommended strategy
```

The model loads assumptions from `configs/base_case.yaml`, evaluates each strategy using modular technical, emissions, and cost models, exports the results to `outputs/tables/baseline_results.csv`, and generates comparison charts in `outputs/figures/`.

## Version 1 Limitations

Version 1 is a baseline proof-of-concept model. It uses annual demand and annual PV generation assumptions, so it does not yet capture hourly load-solar mismatch, grid import/export, curtailment, or battery dispatch.

It also uses one representative rooftop PV technology and deterministic assumptions. Future versions will add hourly physical modelling, PV + ESS simulation, optimisation, sensitivity analysis, policy scenario comparison, and stakeholder-specific recommendations.

## How to Run

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
python -m pytest
```

## Key Results

Recommended Version 1 strategy: Solar PV only
NPV: SGD 1,388,436.70
Emissions reduction: 20.00%
Simple payback: 3.45 years
Discounted payback: 4 years
