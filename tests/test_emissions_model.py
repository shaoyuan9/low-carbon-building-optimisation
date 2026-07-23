import pytest

from src.models.emissions_model import (
    EmissionsInput,
    calculate_baseline_emissions,
    calculate_project_emissions,
    calculate_required_low_carbon_electricity_kwh,
)


def test_baseline_emissions():
    emissions = calculate_baseline_emissions(
        annual_electricity_demand_kwh=1_000_000,
        grid_emission_factor_kgco2_per_kwh=0.4,
    )

    assert emissions == 400_000


def test_project_emissions_with_pv():
    result = calculate_project_emissions(
        EmissionsInput(
            annual_electricity_demand_kwh=1_000_000,
            grid_emission_factor_kgco2_per_kwh=0.4,
            pv_used_onsite_kwh=200_000,
            renewable_purchase_kwh=0,
        ),
        target_reduction_percent=0.20,
    )

    assert result.baseline_emissions_kgco2 == 400_000
    assert result.project_emissions_kgco2 == 320_000
    assert result.emissions_reduction_kgco2 == 80_000
    assert result.emissions_reduction_percent == pytest.approx(0.20)
    assert result.target_met is True
    assert result.remaining_emissions_gap_kgco2 == 0


def test_project_emissions_with_pv_and_renewable_purchase():
    result = calculate_project_emissions(
        EmissionsInput(
            annual_electricity_demand_kwh=1_000_000,
            grid_emission_factor_kgco2_per_kwh=0.4,
            pv_used_onsite_kwh=100_000,
            renewable_purchase_kwh=100_000,
        ),
        target_reduction_percent=0.20,
    )

    assert result.project_emissions_kgco2 == 320_000
    assert result.emissions_reduction_kgco2 == 80_000
    assert result.emissions_reduction_percent == pytest.approx(0.20)
    assert result.target_met is True


def test_required_low_carbon_electricity():
    required = calculate_required_low_carbon_electricity_kwh(
        annual_electricity_demand_kwh=1_000_000,
        target_reduction_percent=0.20,
    )

    assert required == 200_000


def test_project_emissions_caps_low_carbon_inputs_at_demand():
    result = calculate_project_emissions(
        EmissionsInput(
            annual_electricity_demand_kwh=1_000_000,
            grid_emission_factor_kgco2_per_kwh=0.4,
            pv_used_onsite_kwh=900_000,
            renewable_purchase_kwh=900_000,
        ),
        target_reduction_percent=0.20,
    )

    assert result.project_emissions_kgco2 == 0
    assert result.emissions_reduction_percent == pytest.approx(1.0)
    assert result.target_met is True


def test_emissions_rejects_invalid_target():
    with pytest.raises(ValueError):
        calculate_project_emissions(
            EmissionsInput(
                annual_electricity_demand_kwh=1_000_000,
                grid_emission_factor_kgco2_per_kwh=0.4,
            ),
            target_reduction_percent=1.5,
        )
