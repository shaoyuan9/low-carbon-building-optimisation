# main.py
# does not contain modelling logic. It orchestrates everything.

from pathlib import Path

from src.analysis.baseline_analysis import (
    baseline_results_to_dataframe,
    run_baseline_analysis,
    select_recommended_strategy,
)
from src.inputs.config_loader import load_baseline_input_from_yaml
from src.visualisation.plots import generate_baseline_figures


def main() -> None:
    print("Starting Version 1 baseline analysis...")

    config_path = Path("configs/base_case.yaml") # set file paths and output folders           
    output_tables_dir = Path("outputs/tables")
    output_figures_dir = Path("outputs/figures/version_1")

    output_tables_dir.mkdir(parents=True, exist_ok=True)
    output_figures_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading config from: {config_path.resolve()}")

    analysis_input = load_baseline_input_from_yaml(config_path) # loads YAML assumption 

    print("Running baseline strategy comparison...")

    results = run_baseline_analysis(analysis_input) # run analysis and convert to DataFrame 
    results_df = baseline_results_to_dataframe(results)

    output_file = output_tables_dir / "baseline_results.csv" # export baseline results to CSV
    results_df.to_csv(output_file, index=False)

    figure_paths = generate_baseline_figures( # generate output figures
        dataframe=results_df,
        output_dir=output_figures_dir,
    )

    print("\nBaseline analysis completed.")
    print(f"Results saved to: {output_file.resolve()}")

    print("\nFigures saved:")
    for figure_name, figure_path in figure_paths.items():
        print(f"- {figure_name}: {figure_path.resolve()}")

    summary_columns = [ # print a readable summary table 
        "strategy_name",
        "pv_capacity_kwp",
        "pv_generation_year1_kwh",
        "renewable_purchase_kwh_per_year",
        "emissions_reduction_percent",
        "target_met_label",
        "pv_capex_sgd",
        "annual_net_savings_year1_sgd",
        "npv_sgd",
        "simple_payback_years",
        "discounted_payback_years",
    ]

    print("\nSummary table:")
    print(results_df[summary_columns].to_string(index=False))

    recommended_strategy = select_recommended_strategy(results) # print the recommended strategy 

    if recommended_strategy is not None:
        print("\nRecommended Version 1 strategy:")
        print(f"- {recommended_strategy.strategy_name}")
        print(f"- NPV: SGD {recommended_strategy.npv_sgd:,.2f}")
        print(
            "- Emissions reduction: "
            f"{recommended_strategy.emissions_reduction_percent * 100:.2f}%"
        )
    else:
        print("\nNo strategy met the emissions reduction target.")


if __name__ == "__main__":
    main()