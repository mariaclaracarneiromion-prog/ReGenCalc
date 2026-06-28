from pydantic import BaseModel
from typing import List, Optional


class RouteRequest(BaseModel):
    origin: str
    destination: str
    vehicle_type: str = "car"
    vehicle_mass: Optional[float] = None


class Segment(BaseModel):
    distance: float
    duration: float
    surface: str
    iri: float
    coordinates: List[List[float]]


class EnergyResult(BaseModel):
    method_name: str
    energy_wh: float
    description: str


class RouteResponse(BaseModel):
    total_distance_km: float
    total_duration_min: float
    segments: List[Segment]
    energy_method_1: EnergyResult
    energy_method_2: EnergyResult
    energy_method_3: EnergyResult
    energy_average: float
    energy_min: float
    energy_max: float
    comparisons: dict