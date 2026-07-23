# src/models/emissions_model.py
# handles carbon accounting and emissions reduction calculations
# calculates baseline emissions, project emissions, emissions reduction, if emission target met, and remaining emissions gap.

from dataclasses import dataclass


@dataclass(frozen=True)
class EmissionsInput:
    annual_electricity_demand_kwh: float
    grid_emission_factor_kgco2_per_kwh: float

    # Low-carbon electricity sources
    pv_used_onsite_kwh: float = 0.0
    renewable_purchase_kwh: float = 0.0

    # Version 1 assumes renewable electricity purchase is treated as zero-emission.
    # You can change this later if you want to model residual emissions.
    renewable_emission_factor_kgco2_per_kwh: float = 0.0


@dataclass(frozen=True)
class EmissionsResult:
    baseline_emissions_kgco2: float
    project_emissions_kgco2: float
    emissions_reduction_kgco2: float
    emissions_reduction_percent: float
    target_reduction_percent: float
    target_met: bool
    remaining_emissions_gap_kgco2: float


def calculate_baseline_emissions( # helper function 
    annual_electricity_demand_kwh: float,
    grid_emission_factor_kgco2_per_kwh: float,
) -> float:
    """
    Calculate baseline emissions if all electricity comes from the grid.
    """
    if annual_electricity_demand_kwh < 0:
        raise ValueError("annual_electricity_demand_kwh cannot be negative.")

    if grid_emission_factor_kgco2_per_kwh < 0:
        raise ValueError("grid_emission_factor_kgco2_per_kwh cannot be negative.")

    return annual_electricity_demand_kwh * grid_emission_factor_kgco2_per_kwh


def calculate_project_emissions(
    emissions_input: EmissionsInput,
    target_reduction_percent: float,
) -> EmissionsResult:
    """
    Calculate emissions after PV and renewable electricity purchase.

    Version 1 annual logic:
    - PV generation used onsite reduces grid electricity.
    - Renewable electricity purchase reduces remaining grid electricity.
    - Final grid consumption causes emissions 
    """
    if not 0 <= target_reduction_percent <= 1:
        raise ValueError("target_reduction_percent must be between 0 and 1.")

    annual_demand = emissions_input.annual_electricity_demand_kwh

    if annual_demand < 0:
        raise ValueError("annual_electricity_demand_kwh cannot be negative.")

    if emissions_input.pv_used_onsite_kwh < 0:
        raise ValueError("pv_used_onsite_kwh cannot be negative.")

    if emissions_input.renewable_purchase_kwh < 0:
        raise ValueError("renewable_purchase_kwh cannot be negative.")

    baseline_emissions = calculate_baseline_emissions(
        annual_electricity_demand_kwh=annual_demand,
        grid_emission_factor_kgco2_per_kwh=emissions_input.grid_emission_factor_kgco2_per_kwh,
    )

    pv_used = min(emissions_input.pv_used_onsite_kwh, annual_demand) # cap PV and renewable purchase so they do not exceed annual demand
    remaining_demand_after_pv = max(annual_demand - pv_used, 0)

    renewable_purchase = min(
        emissions_input.renewable_purchase_kwh,
        remaining_demand_after_pv,
    )

    final_grid_consumption = max(
        annual_demand - pv_used - renewable_purchase,
        0,
    )

    project_emissions = (
        final_grid_consumption * emissions_input.grid_emission_factor_kgco2_per_kwh
        + renewable_purchase
        * emissions_input.renewable_emission_factor_kgco2_per_kwh
    )

    emissions_reduction = baseline_emissions - project_emissions 

    if baseline_emissions == 0:
        emissions_reduction_percent = 0.0
    else:
        emissions_reduction_percent = emissions_reduction / baseline_emissions

    target_emissions = baseline_emissions * (1 - target_reduction_percent)

    remaining_emissions_gap = max(project_emissions - target_emissions, 0)

    return EmissionsResult( # output data returned as a dataclass in emissions_model.py
        baseline_emissions_kgco2=baseline_emissions,
        project_emissions_kgco2=project_emissions,
        emissions_reduction_kgco2=emissions_reduction,
        emissions_reduction_percent=emissions_reduction_percent,
        target_reduction_percent=target_reduction_percent,
        target_met=emissions_reduction_percent >= target_reduction_percent,
        remaining_emissions_gap_kgco2=remaining_emissions_gap,
    )


def calculate_required_low_carbon_electricity_kwh( # main function 2 
    annual_electricity_demand_kwh: float,
    target_reduction_percent: float,
) -> float:
    """
    In Version 1, assuming low-carbon electricity has zero operational emissions,
    the required low-carbon electricity is approximately target % of demand.
    """
    if annual_electricity_demand_kwh < 0:
        raise ValueError("annual_electricity_demand_kwh cannot be negative.")

    if not 0 <= target_reduction_percent <= 1:
        raise ValueError("target_reduction_percent must be between 0 and 1.")

    return annual_electricity_demand_kwh * target_reduction_percent