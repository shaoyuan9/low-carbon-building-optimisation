# src/models/load_model.py
# calculates building annual electricity demand, peak hourly demand, average hourly demand, and number of hours. 

from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True)
class LoadInput: # define LoadInput 
    """
    Input data for building electricity demand.

    Use either:
    - annual_electricity_demand_kwh, or
    - hourly_load_kwh

    If hourly_load_kwh is provided, the annual demand is calculated from it.
    """
    annual_electricity_demand_kwh: Optional[float] = None
    hourly_load_kwh: Optional[Sequence[float]] = None


@dataclass(frozen=True)
class LoadResult: # define LoadResult
    annual_electricity_demand_kwh: float
    peak_hourly_demand_kwh: Optional[float]
    average_hourly_demand_kwh: Optional[float]
    number_of_hours: Optional[int]
    data_source: str


def calculate_load_profile(load_input: LoadInput) -> LoadResult:
    """
    Calculate annual electricity demand and basic load statistics.

    For Version 1, annual demand is enough.
    For Version 2, hourly load will become more important.
    """
    if load_input.hourly_load_kwh is not None: # handle hourly input: sum it, calculate peak, average, and number of hours.
        hourly_load = list(load_input.hourly_load_kwh)

        if len(hourly_load) == 0:
            raise ValueError("hourly_load_kwh cannot be empty.")

        if any(value < 0 for value in hourly_load):
            raise ValueError("hourly_load_kwh cannot contain negative values.")

        annual_demand = sum(hourly_load)

        return LoadResult( # output data returned as a dataclass in load_model.py
            annual_electricity_demand_kwh=annual_demand,
            peak_hourly_demand_kwh=max(hourly_load),
            average_hourly_demand_kwh=annual_demand / len(hourly_load),
            number_of_hours=len(hourly_load),
            data_source="hourly_load_profile",
        )

    if load_input.annual_electricity_demand_kwh is not None: # handle annual input: return annual demand directly.
        if load_input.annual_electricity_demand_kwh <= 0:
            raise ValueError("annual_electricity_demand_kwh must be positive.")

        return LoadResult( # output data returned as a dataclass in load_model.py
            annual_electricity_demand_kwh=load_input.annual_electricity_demand_kwh,
            peak_hourly_demand_kwh=None,
            average_hourly_demand_kwh=None,
            number_of_hours=None,
            data_source="annual_input",
        )

    raise ValueError(
        "Either annual_electricity_demand_kwh or hourly_load_kwh must be provided."
    )