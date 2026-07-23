import pytest

from src.models.load_model import LoadInput, calculate_load_profile


def test_load_model_with_annual_demand():
    result = calculate_load_profile(
        LoadInput(annual_electricity_demand_kwh=1_000_000)
    )

    assert result.annual_electricity_demand_kwh == 1_000_000
    assert result.peak_hourly_demand_kwh is None
    assert result.average_hourly_demand_kwh is None
    assert result.number_of_hours is None
    assert result.data_source == "annual_input"


def test_load_model_with_hourly_load():
    result = calculate_load_profile(
        LoadInput(hourly_load_kwh=[100, 200, 300])
    )

    assert result.annual_electricity_demand_kwh == 600
    assert result.peak_hourly_demand_kwh == 300
    assert result.average_hourly_demand_kwh == 200
    assert result.number_of_hours == 3
    assert result.data_source == "hourly_load_profile"


def test_load_model_rejects_negative_annual_demand():
    with pytest.raises(ValueError):
        calculate_load_profile(
            LoadInput(annual_electricity_demand_kwh=-100)
        )


def test_load_model_rejects_negative_hourly_load():
    with pytest.raises(ValueError):
        calculate_load_profile(LoadInput(hourly_load_kwh=[100, -50, 200]))


def test_load_model_requires_one_input():
    with pytest.raises(ValueError):
        calculate_load_profile(LoadInput())
