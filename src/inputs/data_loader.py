# src/inputs/data_loader.py
# mostly future-facing, not used in Version 1 yet. 

from pathlib import Path
from typing import Iterable

import pandas as pd


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Load a CSV file as a pandas DataFrame.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    return pd.read_csv(file_path)


def validate_required_columns(
    dataframe: pd.DataFrame,
    required_columns: Iterable[str],
    dataset_name: str = "dataset",
) -> None:
    """
    Check that a DataFrame contains all required columns.
    """
    missing_columns = set(required_columns) - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing required columns: "
            f"{sorted(missing_columns)}"
        )


def load_building_load_profile(file_path: str | Path) -> pd.DataFrame:
    """
    Load building load profile.

    Version 1 may not need this yet if using annual demand from YAML.
    Version 2 will use this for hourly energy balance.
    """
    dataframe = load_csv(file_path)

    validate_required_columns(
        dataframe=dataframe,
        required_columns=["timestamp", "load_kwh"],
        dataset_name="building_load_profile",
    )

    return dataframe


def load_electricity_prices(file_path: str | Path) -> pd.DataFrame:
    """
    Load electricity price data.

    Version 1 may use a single price from YAML.
    Later versions can use time-varying prices.
    """
    dataframe = load_csv(file_path)

    validate_required_columns(
        dataframe=dataframe,
        required_columns=["timestamp", "electricity_price_sgd_per_kwh"],
        dataset_name="electricity_prices",
    )

    return dataframe


def load_grid_emission_factor(file_path: str | Path) -> pd.DataFrame:
    """
    Load grid emission factor data.
    """
    dataframe = load_csv(file_path)

    validate_required_columns(
        dataframe=dataframe,
        required_columns=["year", "grid_emission_factor_kgco2_per_kwh"],
        dataset_name="grid_emission_factor",
    )

    return dataframe


def load_pv_technology_costs(file_path: str | Path) -> pd.DataFrame:
    """
    Load PV technology cost assumptions.

    Version 1 can use one representative PV type.
    Later versions can compare different PV technologies.
    """
    dataframe = load_csv(file_path)

    validate_required_columns(
        dataframe=dataframe,
        required_columns=[
            "technology_name",
            "pv_capex_sgd_per_kwp",
            "pv_opex_fraction_of_capex_per_year",
            "pv_annual_yield_kwh_per_kwp",
            "pv_degradation_rate_per_year",
            "area_required_m2_per_kwp",
        ],
        dataset_name="pv_technology_costs",
    )

    return dataframe
