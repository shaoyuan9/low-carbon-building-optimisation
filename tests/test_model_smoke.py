from src.models.load_model import LoadInput, calculate_load_profile
from src.models.emissions_model import EmissionsInput, calculate_project_emissions
from src.models.cost_model import CostInput, calculate_costs
from src.models.solar_pv_model import SolarPVInput, calculate_solar_pv_generation


def test_four_models_work_together():
    # 1. Load model
    load_result = calculate_load_profile(
        LoadInput(annual_electricity_demand_kwh=1_000_000)
    )

    # 2. Solar PV model
    solar_result = calculate_solar_pv_generation(
        SolarPVInput(
            pv_capacity_kwp=500,
            annual_yield_kwh_per_kwp=1200,
            project_lifetime_years=25,
            degradation_rate_per_year=0.005,
            rooftop_area_m2=5000,
            area_required_m2_per_kwp=5,
        )
    )

    # Version 1 assumption:
    # all PV generation is used onsite up to annual demand.
    pv_used_onsite = min(
        solar_result.annual_generation_year1_kwh,
        load_result.annual_electricity_demand_kwh,
    )

    # 3. Emissions model
    emissions_result = calculate_project_emissions(
        EmissionsInput(
            annual_electricity_demand_kwh=load_result.annual_electricity_demand_kwh,
            grid_emission_factor_kgco2_per_kwh=0.4,
            pv_used_onsite_kwh=pv_used_onsite,
            renewable_purchase_kwh=0,
        ),
        target_reduction_percent=0.20,
    )

    # 4. Cost model
    cost_result = calculate_costs(
        CostInput(
            annual_electricity_demand_kwh=load_result.annual_electricity_demand_kwh,
            electricity_price_sgd_per_kwh=0.25,
            project_lifetime_years=25,
            discount_rate=0.05,
            pv_capacity_kwp=solar_result.pv_capacity_kwp,
            pv_capex_sgd_per_kwp=1200,
            pv_opex_fraction_of_capex_per_year=0.01,
            pv_generation_used_onsite_year1_kwh=pv_used_onsite,
            renewable_purchase_kwh_per_year=0,
            renewable_premium_sgd_per_kwh=0.03,
        )
    )

    assert load_result.annual_electricity_demand_kwh == 1_000_000
    assert solar_result.annual_generation_year1_kwh == 600_000
    assert emissions_result.emissions_reduction_percent >= 0.20
    assert cost_result.pv_capex_sgd == 600_000
    assert cost_result.annual_net_savings_year1_sgd > 0
    assert cost_result.npv_sgd > 0
