import pytest

from src.models.cost_model import (
    CostInput,
    calculate_costs,
    calculate_present_value_of_annual_amount,
)


def test_present_value_of_annual_amount():
    pv = calculate_present_value_of_annual_amount(
        annual_amount_sgd=1000,
        discount_rate=0.05,
        project_lifetime_years=2,
    )

    expected = 1000 / 1.05 + 1000 / (1.05**2)
    assert pv == pytest.approx(expected)


def test_cost_model_with_pv():
    result = calculate_costs(
        CostInput(
            annual_electricity_demand_kwh=1_000_000,
            electricity_price_sgd_per_kwh=0.25,
            project_lifetime_years=25,
            discount_rate=0.05,
            pv_capacity_kwp=500,
            pv_capex_sgd_per_kwp=1200,
            pv_opex_fraction_of_capex_per_year=0.01,
            pv_generation_used_onsite_year1_kwh=600_000,
            renewable_purchase_kwh_per_year=0,
            renewable_premium_sgd_per_kwh=0.03,
        )
    )

    assert result.baseline_annual_grid_cost_year1_sgd == 250_000
    assert result.project_annual_grid_cost_year1_sgd == 100_000
    assert result.pv_capex_sgd == 600_000
    assert result.annual_pv_opex_year1_sgd == 6_000
    assert result.annual_electricity_savings_year1_sgd == 150_000
    assert result.annual_net_savings_year1_sgd == 144_000
    assert result.npv_sgd > 0
    assert result.simple_payback_years == pytest.approx(600_000 / 144_000)
    assert result.discounted_payback_years is not None
    assert result.pv_lcoe_sgd_per_kwh is not None
    assert result.lifetime_net_savings_sgd > 0


def test_cost_model_with_renewable_purchase_only():
    result = calculate_costs(
        CostInput(
            annual_electricity_demand_kwh=1_000_000,
            electricity_price_sgd_per_kwh=0.25,
            project_lifetime_years=25,
            discount_rate=0.05,
            pv_capacity_kwp=0,
            pv_generation_used_onsite_year1_kwh=0,
            renewable_purchase_kwh_per_year=200_000,
            renewable_premium_sgd_per_kwh=0.03,
        )
    )

    assert result.baseline_annual_grid_cost_year1_sgd == 250_000
    assert result.project_annual_grid_cost_year1_sgd == 250_000
    assert result.annual_electricity_savings_year1_sgd == 0
    assert result.annual_renewable_purchase_premium_year1_sgd == 6_000
    assert result.annual_net_savings_year1_sgd == -6_000
    assert result.pv_capex_sgd == 0
    assert result.npv_sgd < 0
    assert result.simple_payback_years is None
    assert result.discounted_payback_years is None
    assert result.pv_lcoe_sgd_per_kwh is None


def test_cost_model_rejects_negative_pv_capacity():
    with pytest.raises(ValueError):
        calculate_costs(
            CostInput(
                annual_electricity_demand_kwh=1_000_000,
                electricity_price_sgd_per_kwh=0.25,
                project_lifetime_years=25,
                discount_rate=0.05,
                pv_capacity_kwp=-1,
            )
        )
