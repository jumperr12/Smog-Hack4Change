from pydantic import BaseModel


class GeoPoint(BaseModel):
    lat: float
    lon: float


class BBox(BaseModel):
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float
