## Version 1 Logic Flow

Version 1 establishes the base techno-economic model for comparing low-carbon electricity strategies for a Singapore commercial building owner. The objective is to determine and compare how a building can achieve at least 20% electricity-related emissions reduction using a combination of grid electricity, renewable electricity purchase, and rooftop solar PV.

The model follows a modular workflow:

```text
base_case.yaml
    ↓
config_loader.py
    ↓
main.py
    ↓
baseline_analysis.py
    ↓
load_model.py
solar_pv_model.py
emissions_model.py
cost_model.py
    ↓
baseline_results.csv
    ↓
plots.py
    ↓
baseline figures
```

The process begins with `configs/base_case.yaml`, which stores the key assumptions for the base case, including annual electricity demand, electricity tariff, grid emissions factor, PV cost, PV yield, discount rate, project lifetime, rooftop area, and renewable electricity purchase premium.

`config_loader.py` loads these assumptions and converts them into a structured `BaselineAnalysisInput` object. This ensures that the model is configuration-driven rather than dependent on hard-coded assumptions inside the main script.

`main.py` acts as the workflow controller. It loads the configuration, runs the baseline analysis, exports the result table, generates charts, and prints a summary of the strategy comparison.

`baseline_analysis.py` compares four baseline strategies:

1. Grid baseline
2. Renewable electricity purchase only
3. Solar PV only
4. Solar PV + renewable electricity purchase

Each strategy is evaluated using the core model components:

* `load_model.py` calculates annual electricity demand.
* `solar_pv_model.py` estimates annual and lifetime PV generation and checks rooftop feasibility.
* `emissions_model.py` calculates baseline emissions, project emissions, emissions reduction percentage, and whether the 20% target is met.
* `cost_model.py` calculates grid electricity cost, PV CAPEX, PV OPEX, renewable purchase premium, annual net savings, NPV, simple payback, discounted payback, and PV LCOE.

The model then produces `outputs/tables/baseline_results.csv`, which summarizes the technical, economic, and emissions performance of each strategy. The visualisation module generates charts such as the cost-emissions comparison, NPV by strategy, and emissions reduction by strategy.

The recommended Version 1 strategy is selected from the strategies that meet the emissions reduction target, using highest NPV as the decision rule. This provides a simple but useful first decision-support output before adding hourly modelling, battery storage, optimisation, uncertainty analysis, and policy scenarios in later versions.
