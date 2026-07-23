# src/inputs/config_loader.py

from pathlib import Path
from typing import Any

import yaml

from src.analysis.baseline_analysis import BaselineAnalysisInput


def load_yaml_config(config_path: str | Path) -> dict[str, Any]: 
    """
    Load a YAML configuration file.

    This function only loads the file and returns a dictionary.
    It does not run any modelling logic.
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if config is None:
        raise ValueError(f"Config file is empty: {config_path}")

    return config


def _get_required(config: dict[str, Any], section: str, key: str) -> Any:
    """
    Safely retrieve a required value from the config. Forces every needed key to exist.
    """
    if section not in config:
        raise KeyError(f"Missing config section: {section}")

    if key not in config[section]:
        raise KeyError(f"Missing config key: {section}.{key}")

    return config[section][key]


def build_baseline_input_from_config(
    config: dict[str, Any],
) -> BaselineAnalysisInput:
    """
    Convert the base_case.yaml dictionary (YAML) into BaselineAnalysisInput (Python Object).

    This keeps main.py clean and prevents assumptions from being hard-coded.
    """
    return BaselineAnalysisInput(
        annual_electricity_demand_kwh=_get_required(
            config, "building", "annual_electricity_demand_kwh"
        ),
        electricity_price_sgd_per_kwh=_get_required(
            config, "grid", "electricity_price_sgd_per_kwh"
        ),
        grid_emission_factor_kgco2_per_kwh=_get_required(
            config, "grid", "grid_emission_factor_kgco2_per_kwh"
        ),
        target_reduction_percent=_get_required(
            config, "project", "target_reduction_percent"
        ),
        project_lifetime_years=_get_required(
            config, "project", "project_lifetime_years"
        ),
        discount_rate=_get_required(
            config, "project", "discount_rate"
        ),
        pv_capex_sgd_per_kwp=_get_required(
            config, "solar_pv", "pv_capex_sgd_per_kwp"
        ),
        pv_opex_fraction_of_capex_per_year=_get_required(
            config, "solar_pv", "pv_opex_fraction_of_capex_per_year"
        ),
        pv_annual_yield_kwh_per_kwp=_get_required(
            config, "solar_pv", "pv_annual_yield_kwh_per_kwp"
        ),
        pv_degradation_rate_per_year=_get_required(
            config, "solar_pv", "pv_degradation_rate_per_year"
        ),
        renewable_premium_sgd_per_kwh=_get_required(
            config, "renewable_purchase", "renewable_premium_sgd_per_kwh"
        ),
        rooftop_area_m2=_get_required(
            config, "building", "rooftop_area_m2"
        ),
        area_required_m2_per_kwp=_get_required(
            config, "solar_pv", "area_required_m2_per_kwp"
        ),
        electricity_price_escalation_rate_per_year=_get_required(
            config, "grid", "electricity_price_escalation_rate_per_year"
        ),
        pv_opex_escalation_rate_per_year=_get_required(
            config, "solar_pv", "pv_opex_escalation_rate_per_year"
        ),
        renewable_premium_escalation_rate_per_year=_get_required(
            config,
            "renewable_purchase",
            "renewable_premium_escalation_rate_per_year",
        ),
        hybrid_pv_share_of_target=_get_required(
            config, "baseline_analysis", "hybrid_pv_share_of_target"
        ),
    )


def load_baseline_input_from_yaml( 
    config_path: str | Path,
) -> BaselineAnalysisInput:
    """
    Load base case YAML and return BaselineAnalysisInput in one convinient function.
    """
    config = load_yaml_config(config_path)
    return build_baseline_input_from_config(config)
