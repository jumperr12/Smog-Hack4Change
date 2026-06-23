from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Station(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    city: str


class AirQualitySample(BaseModel):
    lat: float
    lon: float
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    aqi_index: Optional[str] = None
    source: str
    timestamp: Optional[datetime] = None
