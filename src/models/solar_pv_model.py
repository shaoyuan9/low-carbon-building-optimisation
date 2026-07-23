# src/models/solar_pv_model.py
# estimates PV generation and checks if the required PV capacity fits the roof area.
# calculates pv capacity, annual generation for year 1, lifetime generation, degradation rate, project lifetime, max capacity by area, and feasibility of area constraint.

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True) # define PV inputs 
class SolarPVInput:
    pv_capacity_kwp: float
    annual_yield_kwh_per_kwp: float
    project_lifetime_years: int
    degradation_rate_per_year: float = 0.005

    # Optional roof-area constraint
    rooftop_area_m2: Optional[float] = None
    area_required_m2_per_kwp: Optional[float] = None


@dataclass(frozen=True) # define outputs 
class SolarPVResult: 
    pv_capacity_kwp: float
    annual_generation_year1_kwh: float
    lifetime_generation_kwh: float
    degradation_rate_per_year: float
    project_lifetime_years: int
    max_capacity_by_area_kwp: Optional[float]
    is_area_feasible: Optional[bool]


def calculate_max_pv_capacity_by_area( # helper function
    rooftop_area_m2: float,
    area_required_m2_per_kwp: float,
) -> float:
    """
    Calculate maximum PV capacity allowed by rooftop area.
    """
    if rooftop_area_m2 <= 0:
        raise ValueError("rooftop_area_m2 must be positive.")

    if area_required_m2_per_kwp <= 0:
        raise ValueError("area_required_m2_per_kwp must be positive.")

    return rooftop_area_m2 / area_required_m2_per_kwp


def calculate_lifetime_pv_generation( # helper function 
    annual_generation_year1_kwh: float,
    degradation_rate_per_year: float,
    project_lifetime_years: int,
) -> float:
    """
    Calculate lifetime PV generation with annual degradation.
    """
    if annual_generation_year1_kwh < 0:
        raise ValueError("annual_generation_year1_kwh cannot be negative.")

    if not 0 <= degradation_rate_per_year < 1:
        raise ValueError("degradation_rate_per_year must be between 0 and 1.")

    if project_lifetime_years <= 0:
        raise ValueError("project_lifetime_years must be positive.")

    lifetime_generation = 0.0

    for year in range(project_lifetime_years):
        yearly_generation = annual_generation_year1_kwh * (
            (1 - degradation_rate_per_year) ** year # formula to calculate yearly generation with degradation
        )
        lifetime_generation += yearly_generation # total of all yearly generations 

    return lifetime_generation


def calculate_solar_pv_generation(pv_input: SolarPVInput) -> SolarPVResult: # main function 
    """
    Calculate annual and lifetime PV generation.

    Version 1 uses annual generation.
    Later versions can replace this with hourly solar generation.
    """
    if pv_input.pv_capacity_kwp < 0:
        raise ValueError("pv_capacity_kwp cannot be negative.")

    if pv_input.annual_yield_kwh_per_kwp <= 0:
        raise ValueError("annual_yield_kwh_per_kwp must be positive.")

    annual_generation_year1 = (
        pv_input.pv_capacity_kwp * pv_input.annual_yield_kwh_per_kwp
    ) # Annual Generation = PV Capacity × PV Yield

    lifetime_generation = calculate_lifetime_pv_generation(
        annual_generation_year1_kwh=annual_generation_year1,
        degradation_rate_per_year=pv_input.degradation_rate_per_year,
        project_lifetime_years=pv_input.project_lifetime_years,
    )

    max_capacity_by_area = None
    is_area_feasible = None

    if (
        pv_input.rooftop_area_m2 is not None
        and pv_input.area_required_m2_per_kwp is not None
    ):
        max_capacity_by_area = calculate_max_pv_capacity_by_area(
            rooftop_area_m2=pv_input.rooftop_area_m2,
            area_required_m2_per_kwp=pv_input.area_required_m2_per_kwp,
        )
        is_area_feasible = pv_input.pv_capacity_kwp <= max_capacity_by_area # checks if the required PV capacity fits the roof 

    return SolarPVResult( # results returned as a dataclass in solar_pv_model.py
        pv_capacity_kwp=pv_input.pv_capacity_kwp,
        annual_generation_year1_kwh=annual_generation_year1,
        lifetime_generation_kwh=lifetime_generation,
        degradation_rate_per_year=pv_input.degradation_rate_per_year,
        project_lifetime_years=pv_input.project_lifetime_years,
        max_capacity_by_area_kwp=max_capacity_by_area,
        is_area_feasible=is_area_feasible,
    )