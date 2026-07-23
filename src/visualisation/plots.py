# src/visualisation/plots.py

import os
from pathlib import Path
from typing import Iterable

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(__file__).resolve().parents[2] / ".matplotlib_cache"),
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


REQUIRED_BASELINE_COLUMNS = {
    "strategy_name",
    "emissions_reduction_percent",
    "annual_net_savings_year1_sgd",
    "npv_sgd",
    "pv_capex_sgd",
    "target_met_label",
}


def _validate_columns(dataframe: pd.DataFrame, required_columns: Iterable[str]) -> None:
    """
    Check that the DataFrame contains the required columns for plotting.
    """
    missing_columns = set(required_columns) - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns for plotting: {sorted(missing_columns)}"
        )


def _prepare_output_path(output_path: str | Path) -> Path:
    """
    Ensure the parent folder exists before saving a figure.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def _format_strategy_labels(strategy_names: pd.Series) -> list[str]:
    """
    Make long strategy names easier to read in charts.
    """
    replacements = {
        "Grid baseline": "Grid\nbaseline",
        "Renewable electricity purchase only": "Renewable\npurchase",
        "Solar PV only": "Solar PV\nonly",
        "Solar PV + renewable electricity purchase": "Solar PV +\nrenewable purchase",
    }

    return [replacements.get(name, name) for name in strategy_names]


def plot_cost_emissions_comparison(
    dataframe: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """
    Create a cost-emissions comparison scatter plot.

    X-axis:
    - Emissions reduction %

    Y-axis:
    - Annual net savings in year 1

    This is the main Version 1 decision chart.
    """
    _validate_columns(dataframe, REQUIRED_BASELINE_COLUMNS)
    output_path = _prepare_output_path(output_path)

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.scatter(
        dataframe["emissions_reduction_percent"],
        dataframe["annual_net_savings_year1_sgd"],
        s=90,
    )

    for _, row in dataframe.iterrows():
        ax.annotate(
            row["strategy_name"],
            (
                row["emissions_reduction_percent"],
                row["annual_net_savings_year1_sgd"],
            ),
            textcoords="offset points",
            xytext=(8, 6),
            ha="left",
            fontsize=9,
        )

    ax.axvline(
        x=20,
        linestyle="--",
        linewidth=1,
    )

    ax.set_title("Cost-emissions comparison of baseline strategies")
    ax.set_xlabel("Emissions reduction (%)")
    ax.set_ylabel("Annual net savings in year 1 (SGD)")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def plot_npv_by_strategy(
    dataframe: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """
    Create a bar chart comparing NPV by strategy.
    """
    _validate_columns(dataframe, REQUIRED_BASELINE_COLUMNS)
    output_path = _prepare_output_path(output_path)

    plot_data = dataframe.copy()
    plot_data = plot_data.sort_values("npv_sgd", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.barh(
        _format_strategy_labels(plot_data["strategy_name"]),
        plot_data["npv_sgd"],
    )

    ax.axvline(
        x=0,
        linestyle="--",
        linewidth=1,
    )

    ax.set_title("NPV by baseline strategy")
    ax.set_xlabel("NPV (SGD)")
    ax.set_ylabel("Strategy")
    ax.grid(True, axis="x", alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def plot_emissions_reduction_by_strategy(
    dataframe: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """
    Create a bar chart comparing emissions reduction by strategy.
    """
    _validate_columns(dataframe, REQUIRED_BASELINE_COLUMNS)
    output_path = _prepare_output_path(output_path)

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.bar(
        _format_strategy_labels(dataframe["strategy_name"]),
        dataframe["emissions_reduction_percent"],
    )

    ax.axhline(
        y=20,
        linestyle="--",
        linewidth=1,
    )

    ax.set_title("Emissions reduction by baseline strategy")
    ax.set_xlabel("Strategy")
    ax.set_ylabel("Emissions reduction (%)")
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def generate_baseline_figures(
    dataframe: pd.DataFrame,
    output_dir: str | Path = "outputs/figures/version_1",
) -> dict[str, Path]:
    """
    Generate all Version 1 baseline figures.

    Returns a dictionary of figure names and saved file paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    figure_paths = {
        "cost_emissions_comparison": plot_cost_emissions_comparison(
            dataframe=dataframe,
            output_path=output_dir / "cost_emissions_comparison.png",
        ),
        "npv_by_strategy": plot_npv_by_strategy(
            dataframe=dataframe,
            output_path=output_dir / "npv_by_strategy.png",
        ),
        "emissions_reduction_by_strategy": plot_emissions_reduction_by_strategy(
            dataframe=dataframe,
            output_path=output_dir / "emissions_reduction_by_strategy.png",
        ),
    }

    return figure_paths


def load_baseline_results(results_path: str | Path) -> pd.DataFrame:
    """
    Convenience function for loading baseline results from CSV.
    """
    results_path = Path(results_path)

    if not results_path.exists():
        raise FileNotFoundError(f"Could not find baseline results file: {results_path}")

    return pd.read_csv(results_path)
