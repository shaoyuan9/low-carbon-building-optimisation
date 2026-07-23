# src/analysis/baseline_analysis.py
# orchestrate the four core models (this code is the reusable pipeline). 

from dataclasses import asdict, dataclass
from typing import Optional

import pandas as pd

from src.models.cost_model import CostInput, calculate_costs
from src.models.emissions_model import (
    EmissionsInput,
    calculate_project_emissions,
    calculate_required_low_carbon_electricity_kwh,
)
from src.models.load_model import LoadInput, calculate_load_profile
from src.models.solar_pv_model import SolarPVInput, calculate_solar_pv_generation


@dataclass(frozen=True)
class BaselineAnalysisInput:
    """
    Inputs required for Version 1 baseline strategy comparison.

    Version 1 compares:
    1. Grid baseline
    2. Renewable electricity purchase only
    3. Solar PV only
    4. Solar PV + renewable electricity purchase

    Version 1 uses one representative commercial rooftop PV technology.
    """

    annual_electricity_demand_kwh: float
    electricity_price_sgd_per_kwh: float
    grid_emission_factor_kgco2_per_kwh: float

    target_reduction_percent: float

    project_lifetime_years: int
    discount_rate: float

    pv_capex_sgd_per_kwp: float
    pv_opex_fraction_of_capex_per_year: float
    pv_annual_yield_kwh_per_kwp: float
    pv_degradation_rate_per_year: float

    renewable_premium_sgd_per_kwh: float

    rooftop_area_m2: Optional[float] = None
    area_required_m2_per_kwp: Optional[float] = None

    electricity_price_escalation_rate_per_year: float = 0.0
    pv_opex_escalation_rate_per_year: float = 0.0
    renewable_premium_escalation_rate_per_year: float = 0.0

    hybrid_pv_share_of_target: float = 0.5


@dataclass(frozen=True)
class StrategyResult:
    strategy_name: str

    annual_electricity_demand_kwh: float

    pv_capacity_kwp: float
    pv_generation_year1_kwh: float
    pv_used_onsite_year1_kwh: float
    renewable_purchase_kwh_per_year: float

    baseline_emissions_kgco2: float
    project_emissions_kgco2: float
    emissions_reduction_kgco2: float
    emissions_reduction_percent: float
    target_reduction_percent: float
    target_met: bool
    remaining_emissions_gap_kgco2: float

    baseline_annual_grid_cost_year1_sgd: float
    project_annual_grid_cost_year1_sgd: float
    pv_capex_sgd: float
    annual_pv_opex_year1_sgd: float
    annual_renewable_purchase_premium_year1_sgd: float
    annual_electricity_savings_year1_sgd: float
    annual_net_savings_year1_sgd: float

    present_value_of_net_savings_sgd: float
    npv_sgd: float
    simple_payback_years: Optional[float]
    discounted_payback_years: Optional[float]
    pv_lcoe_sgd_per_kwh: Optional[float]

    lifetime_baseline_grid_cost_sgd: float
    lifetime_project_grid_cost_sgd: float
    lifetime_electricity_savings_sgd: float
    lifetime_pv_opex_sgd: float
    lifetime_renewable_purchase_premium_sgd: float
    lifetime_net_savings_sgd: float

    is_area_feasible: Optional[bool]
    notes: str


def _validate_baseline_input(analysis_input: BaselineAnalysisInput) -> None:
    if analysis_input.annual_electricity_demand_kwh <= 0:
        raise ValueError("annual_electricity_demand_kwh must be positive.")

    if analysis_input.electricity_price_sgd_per_kwh < 0:
        raise ValueError("electricity_price_sgd_per_kwh cannot be negative.")

    if analysis_input.grid_emission_factor_kgco2_per_kwh < 0:
        raise ValueError("grid_emission_factor_kgco2_per_kwh cannot be negative.")

    if not 0 <= analysis_input.target_reduction_percent <= 1:
        raise ValueError("target_reduction_percent must be between 0 and 1.")

    if analysis_input.project_lifetime_years <= 0:
        raise ValueError("project_lifetime_years must be positive.")

    if analysis_input.discount_rate <= -1:
        raise ValueError("discount_rate must be greater than -1.")

    if analysis_input.pv_capex_sgd_per_kwp < 0:
        raise ValueError("pv_capex_sgd_per_kwp cannot be negative.")

    if analysis_input.pv_opex_fraction_of_capex_per_year < 0:
        raise ValueError("pv_opex_fraction_of_capex_per_year cannot be negative.")

    if analysis_input.pv_annual_yield_kwh_per_kwp <= 0:
        raise ValueError("pv_annual_yield_kwh_per_kwp must be positive.")

    if not 0 <= analysis_input.pv_degradation_rate_per_year < 1:
        raise ValueError("pv_degradation_rate_per_year must be between 0 and 1.")

    if analysis_input.renewable_premium_sgd_per_kwh < 0:
        raise ValueError("renewable_premium_sgd_per_kwh cannot be negative.")

    if not 0 <= analysis_input.hybrid_pv_share_of_target <= 1:
        raise ValueError("hybrid_pv_share_of_target must be between 0 and 1.")

    if (
        analysis_input.rooftop_area_m2 is not None
        and analysis_input.rooftop_area_m2 <= 0
    ):
        raise ValueError("rooftop_area_m2 must be positive when provided.")

    if (
        analysis_input.area_required_m2_per_kwp is not None
        and analysis_input.area_required_m2_per_kwp <= 0
    ):
        raise ValueError("area_required_m2_per_kwp must be positive when provided.")


def _calculate_max_pv_capacity_kwp(
    analysis_input: BaselineAnalysisInput,
) -> Optional[float]:
    if (
        analysis_input.rooftop_area_m2 is None
        or analysis_input.area_required_m2_per_kwp is None
    ):
        return None

    return analysis_input.rooftop_area_m2 / analysis_input.area_required_m2_per_kwp


def _apply_rooftop_constraint(
    requested_pv_capacity_kwp: float,
    max_pv_capacity_kwp: Optional[float],
) -> tuple[float, bool, str]:
    """
    Returns:
    - final PV capacity used in the model
    - whether the requested capacity was feasible
    - explanatory note
    """
    if max_pv_capacity_kwp is None:
        return requested_pv_capacity_kwp, True, "No rooftop constraint applied."

    if requested_pv_capacity_kwp <= max_pv_capacity_kwp:
        return requested_pv_capacity_kwp, True, "Requested PV capacity is area-feasible."

    return (
        max_pv_capacity_kwp,
        False,
        "Requested PV capacity exceeds rooftop limit; PV capacity capped by available area.",
    )


def _run_single_strategy(
    strategy_name: str,
    analysis_input: BaselineAnalysisInput,
    pv_capacity_kwp: float,
    renewable_purchase_kwh_per_year: float,
    requested_capacity_area_feasible: Optional[bool],
    notes: str,
) -> StrategyResult:
    """
    Run one strategy through the four core model components:
    - load model
    - solar PV model
    - emissions model
    - cost model
    """

    load_result = calculate_load_profile(
        LoadInput(
            annual_electricity_demand_kwh=analysis_input.annual_electricity_demand_kwh
        )
    )

    solar_result = calculate_solar_pv_generation(
        SolarPVInput(
            pv_capacity_kwp=pv_capacity_kwp,
            annual_yield_kwh_per_kwp=analysis_input.pv_annual_yield_kwh_per_kwp,
            project_lifetime_years=analysis_input.project_lifetime_years,
            degradation_rate_per_year=analysis_input.pv_degradation_rate_per_year,
            rooftop_area_m2=analysis_input.rooftop_area_m2,
            area_required_m2_per_kwp=analysis_input.area_required_m2_per_kwp,
        )
    )

    pv_used_onsite_year1 = min(
        solar_result.annual_generation_year1_kwh,
        load_result.annual_electricity_demand_kwh,
    )

    renewable_purchase_kwh_per_year = min( # ensures that PV onsite use + renewable purchase does not exceed annual demand. 
        renewable_purchase_kwh_per_year,
        max(load_result.annual_electricity_demand_kwh - pv_used_onsite_year1, 0),
    )

    emissions_result = calculate_project_emissions(
        EmissionsInput(
            annual_electricity_demand_kwh=load_result.annual_electricity_demand_kwh,
            grid_emission_factor_kgco2_per_kwh=(
                analysis_input.grid_emission_factor_kgco2_per_kwh
            ),
            pv_used_onsite_kwh=pv_used_onsite_year1,
            renewable_purchase_kwh=renewable_purchase_kwh_per_year,
        ),
        target_reduction_percent=analysis_input.target_reduction_percent,
    )

    cost_result = calculate_costs(
        CostInput(
            annual_electricity_demand_kwh=load_result.annual_electricity_demand_kwh,
            electricity_price_sgd_per_kwh=analysis_input.electricity_price_sgd_per_kwh,
            project_lifetime_years=analysis_input.project_lifetime_years,
            discount_rate=analysis_input.discount_rate,
            electricity_price_escalation_rate_per_year=(
                analysis_input.electricity_price_escalation_rate_per_year
            ),
            pv_opex_escalation_rate_per_year=(
                analysis_input.pv_opex_escalation_rate_per_year
            ),
            renewable_premium_escalation_rate_per_year=(
                analysis_input.renewable_premium_escalation_rate_per_year
            ),
            pv_capacity_kwp=solar_result.pv_capacity_kwp,
            pv_capex_sgd_per_kwp=analysis_input.pv_capex_sgd_per_kwp,
            pv_opex_fraction_of_capex_per_year=(
                analysis_input.pv_opex_fraction_of_capex_per_year
            ),
            pv_generation_used_onsite_year1_kwh=pv_used_onsite_year1,
            pv_degradation_rate_per_year=analysis_input.pv_degradation_rate_per_year,
            renewable_purchase_kwh_per_year=renewable_purchase_kwh_per_year,
            renewable_premium_sgd_per_kwh=analysis_input.renewable_premium_sgd_per_kwh,
        )
    )

    return StrategyResult( # combines output from all four models into a single dataclass for reporting.
        strategy_name=strategy_name,
        annual_electricity_demand_kwh=load_result.annual_electricity_demand_kwh,
        pv_capacity_kwp=solar_result.pv_capacity_kwp,
        pv_generation_year1_kwh=solar_result.annual_generation_year1_kwh,
        pv_used_onsite_year1_kwh=pv_used_onsite_year1,
        renewable_purchase_kwh_per_year=renewable_purchase_kwh_per_year,
        baseline_emissions_kgco2=emissions_result.baseline_emissions_kgco2,
        project_emissions_kgco2=emissions_result.project_emissions_kgco2,
        emissions_reduction_kgco2=emissions_result.emissions_reduction_kgco2,
        emissions_reduction_percent=emissions_result.emissions_reduction_percent,
        target_reduction_percent=emissions_result.target_reduction_percent,
        target_met=emissions_result.target_met,
        remaining_emissions_gap_kgco2=emissions_result.remaining_emissions_gap_kgco2,
        baseline_annual_grid_cost_year1_sgd=(
            cost_result.baseline_annual_grid_cost_year1_sgd
        ),
        project_annual_grid_cost_year1_sgd=(
            cost_result.project_annual_grid_cost_year1_sgd
        ),
        pv_capex_sgd=cost_result.pv_capex_sgd,
        annual_pv_opex_year1_sgd=cost_result.annual_pv_opex_year1_sgd,
        annual_renewable_purchase_premium_year1_sgd=(
            cost_result.annual_renewable_purchase_premium_year1_sgd
        ),
        annual_electricity_savings_year1_sgd=(
            cost_result.annual_electricity_savings_year1_sgd
        ),
        annual_net_savings_year1_sgd=cost_result.annual_net_savings_year1_sgd,
        present_value_of_net_savings_sgd=(
            cost_result.present_value_of_net_savings_sgd
        ),
        npv_sgd=cost_result.npv_sgd,
        simple_payback_years=cost_result.simple_payback_years,
        discounted_payback_years=cost_result.discounted_payback_years,
        pv_lcoe_sgd_per_kwh=cost_result.pv_lcoe_sgd_per_kwh,
        lifetime_baseline_grid_cost_sgd=cost_result.lifetime_baseline_grid_cost_sgd,
        lifetime_project_grid_cost_sgd=cost_result.lifetime_project_grid_cost_sgd,
        lifetime_electricity_savings_sgd=cost_result.lifetime_electricity_savings_sgd,
        lifetime_pv_opex_sgd=cost_result.lifetime_pv_opex_sgd,
        lifetime_renewable_purchase_premium_sgd=(
            cost_result.lifetime_renewable_purchase_premium_sgd
        ),
        lifetime_net_savings_sgd=cost_result.lifetime_net_savings_sgd,
        is_area_feasible=requested_capacity_area_feasible,
        notes=notes,
    )


def run_baseline_analysis(
    analysis_input: BaselineAnalysisInput,
) -> list[StrategyResult]:
    """
    Compare Version 1 baseline strategies.

    Strategy set:
    1. Grid baseline
    2. Renewable electricity purchase only
    3. Solar PV only
    4. Solar PV + renewable electricity purchase
    """

    _validate_baseline_input(analysis_input)

    annual_demand = analysis_input.annual_electricity_demand_kwh

    required_low_carbon_kwh = calculate_required_low_carbon_electricity_kwh(
        annual_electricity_demand_kwh=annual_demand,
        target_reduction_percent=analysis_input.target_reduction_percent,
    )

    required_pv_capacity_for_target_kwp = (
        required_low_carbon_kwh / analysis_input.pv_annual_yield_kwh_per_kwp
    )

    max_pv_capacity_kwp = _calculate_max_pv_capacity_kwp(analysis_input)

    pv_only_capacity_kwp, pv_only_area_feasible, pv_only_note = (
        _apply_rooftop_constraint(
            requested_pv_capacity_kwp=required_pv_capacity_for_target_kwp,
            max_pv_capacity_kwp=max_pv_capacity_kwp,
        )
    )

    hybrid_requested_pv_capacity_kwp = (
        required_pv_capacity_for_target_kwp * analysis_input.hybrid_pv_share_of_target
    )

    hybrid_pv_capacity_kwp, hybrid_area_feasible, hybrid_note = (
        _apply_rooftop_constraint(
            requested_pv_capacity_kwp=hybrid_requested_pv_capacity_kwp,
            max_pv_capacity_kwp=max_pv_capacity_kwp,
        )
    )

    hybrid_pv_generation_year1_kwh = (
        hybrid_pv_capacity_kwp * analysis_input.pv_annual_yield_kwh_per_kwp
    )

    hybrid_renewable_purchase_kwh = max(
        required_low_carbon_kwh - hybrid_pv_generation_year1_kwh,
        0,
    )

    results = [
        _run_single_strategy(
            strategy_name="Grid baseline",
            analysis_input=analysis_input,
            pv_capacity_kwp=0.0,
            renewable_purchase_kwh_per_year=0.0,
            requested_capacity_area_feasible=None,
            notes="No low-carbon electricity strategy applied.",
        ),
        _run_single_strategy(
            strategy_name="Renewable electricity purchase only",
            analysis_input=analysis_input,
            pv_capacity_kwp=0.0,
            renewable_purchase_kwh_per_year=required_low_carbon_kwh,
            requested_capacity_area_feasible=None,
            notes="Renewable electricity purchase sized to meet the emissions reduction target.",
        ),
        _run_single_strategy(
            strategy_name="Solar PV only",
            analysis_input=analysis_input,
            pv_capacity_kwp=pv_only_capacity_kwp,
            renewable_purchase_kwh_per_year=0.0,
            requested_capacity_area_feasible=pv_only_area_feasible,
            notes=pv_only_note,
        ),
        _run_single_strategy(
            strategy_name="Solar PV + renewable electricity purchase",
            analysis_input=analysis_input,
            pv_capacity_kwp=hybrid_pv_capacity_kwp,
            renewable_purchase_kwh_per_year=hybrid_renewable_purchase_kwh,
            requested_capacity_area_feasible=hybrid_area_feasible,
            notes=(
                f"{hybrid_note} PV is sized to cover "
                f"{analysis_input.hybrid_pv_share_of_target:.0%} of the target "
                "low-carbon electricity requirement; renewable purchase covers the remaining gap."
            ),
        ),
    ]

    return results


def baseline_results_to_dataframe(results: list[StrategyResult]) -> pd.DataFrame:
    """
    Convert baseline strategy results into a clean DataFrame for reporting/export.
    """

    dataframe = pd.DataFrame([asdict(result) for result in results])

    dataframe["emissions_reduction_percent"] = (
        dataframe["emissions_reduction_percent"] * 100
    )

    dataframe["target_reduction_percent"] = (
        dataframe["strategy_name"].map(
            {
                result.strategy_name: result.target_reduction_percent
                for result in results
            }
        )
    )

    dataframe["target_met_label"] = dataframe["target_met"].map(
        {True: "Yes", False: "No"}
    )

    dataframe["npv_sgd"] = dataframe["npv_sgd"].round(2)
    dataframe["annual_net_savings_year1_sgd"] = (
        dataframe["annual_net_savings_year1_sgd"].round(2)
    )
    dataframe["emissions_reduction_percent"] = (
        dataframe["emissions_reduction_percent"].round(2)
    )

    return dataframe


def select_recommended_strategy(
    results: list[StrategyResult],
) -> Optional[StrategyResult]:
    """
    Select recommended Version 1 strategy.

    Rule:
    - Must meet emissions target.
    - Select the strategy with the highest NPV.

    Later versions can replace this with full lifecycle cost optimisation.
    """

    target_meeting_results = [result for result in results if result.target_met]

    if not target_meeting_results:
        return None

    return max(target_meeting_results, key=lambda result: result.npv_sgd)
