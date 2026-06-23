from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from .geo import GeoPoint


class TransportMode(str, Enum):
    WALKING = "walking"
    CYCLING = "cycling"
    # Przygotowane do rozszerzenia:
    # DRIVING = "driving"
    # PUBLIC_TRANSIT = "public_transit"


class RouteRequest(BaseModel):
    start: GeoPoint
    end: GeoPoint
    mode: TransportMode = TransportMode.WALKING
    # 0 = optymalizuj czas, 1 = optymalizuj czystość powietrza
    pollution_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    alternatives: int = Field(default=3, ge=1, le=5)


class ExposureSamplePoint(BaseModel):
    lat: float
    lon: float
    pm25: Optional[float] = None


class ExposureProfile(BaseModel):
    # Suma (pm25 * długość_segmentu) w μg/m³·m — proxy ekspozycji, nie miara kliniczna
    total_exposure: float
    avg_pm25: Optional[float] = None
    peak_pm25: Optional[float] = None
    sample_count: int
    samples: List[ExposureSamplePoint]


class RouteCandidate(BaseModel):
    geometry: List[List[float]]  # [[lon, lat], ...] — format GeoJSON
    distance_m: float
    duration_s: float
    mode: TransportMode
    exposure: Optional[ExposureProfile] = None
    cost: Optional[float] = None
    is_recommended: bool = False


class RouteResponse(BaseModel):
    request: RouteRequest
    candidates: List[RouteCandidate]
    recommended_index: Optional[int] = None
