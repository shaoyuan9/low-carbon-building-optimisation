import pytest

from src.models.solar_pv_model import (
    SolarPVInput,
    calculate_max_pv_capacity_by_area,
    calculate_solar_pv_generation,
)


def test_solar_pv_generation_year1():
    result = calculate_solar_pv_generation(
        SolarPVInput(
            pv_capacity_kwp=500,
            annual_yield_kwh_per_kwp=1200,
            project_lifetime_years=25,
            degradation_rate_per_year=0.005,
        )
    )

    assert result.annual_generation_year1_kwh == 600_000
    assert result.lifetime_generation_kwh > 0
    assert result.degradation_rate_per_year == 0.005
    assert result.project_lifetime_years == 25


def test_max_pv_capacity_by_area():
    max_capacity = calculate_max_pv_capacity_by_area(
        rooftop_area_m2=5000,
        area_required_m2_per_kwp=5,
    )

    assert max_capacity == 1000


def test_solar_pv_area_feasibility():
    result = calculate_solar_pv_generation(
        SolarPVInput(
            pv_capacity_kwp=800,
            annual_yield_kwh_per_kwp=1200,
            project_lifetime_years=25,
            rooftop_area_m2=5000,
            area_required_m2_per_kwp=5,
        )
    )

    assert result.max_capacity_by_area_kwp == 1000
    assert result.is_area_feasible is True


def test_solar_pv_area_infeasibility():
    result = calculate_solar_pv_generation(
        SolarPVInput(
            pv_capacity_kwp=1200,
            annual_yield_kwh_per_kwp=1200,
            project_lifetime_years=25,
            rooftop_area_m2=5000,
            area_required_m2_per_kwp=5,
        )
    )

    assert result.max_capacity_by_area_kwp == 1000
    assert result.is_area_feasible is False


def test_solar_pv_rejects_negative_capacity():
    with pytest.raises(ValueError):
        calculate_solar_pv_generation(
            SolarPVInput(
                pv_capacity_kwp=-100,
                annual_yield_kwh_per_kwp=1200,
                project_lifetime_years=25,
            )
        )


def test_solar_pv_rejects_non_positive_yield():
    with pytest.raises(ValueError):
        calculate_solar_pv_generation(
            SolarPVInput(
                pv_capacity_kwp=100,
                annual_yield_kwh_per_kwp=0,
                project_lifetime_years=25,
            )
        )
