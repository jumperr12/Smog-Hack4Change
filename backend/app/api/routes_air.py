import logging
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from ..config import settings
from ..models.air_quality import AirQualitySample, Station
from ..models.geo import BBox, GeoPoint
from ..providers.air_quality.base import AirQualityProvider
from .deps import pobierz_provider_jakosci

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/air-quality", tags=["jakość powietrza"])


@router.get("/stations", response_model=List[Station])
async def lista_stacji(
    min_lat: float = Query(default=settings.bbox_min_lat, description="Dolna granica szerokości"),
    min_lon: float = Query(default=settings.bbox_min_lon, description="Lewa granica długości"),
    max_lat: float = Query(default=settings.bbox_max_lat, description="Górna granica szerokości"),
    max_lon: float = Query(default=settings.bbox_max_lon, description="Prawa granica długości"),
    provider: AirQualityProvider = Depends(pobierz_provider_jakosci),
) -> List[Station]:
    """Zwraca stacje pomiarowe GIOŚ w podanym obszarze. Domyślnie Trójmiasto."""
    bbox = BBox(min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon)
    try:
        return await provider.get_stations(bbox)
    except httpx.HTTPStatusError as blad:
        logger.error("Błąd HTTP od GIOŚ: %s", blad.response.status_code)
        raise HTTPException(502, f"API GIOŚ zwróciło błąd {blad.response.status_code}")
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.TimeoutException):
        logger.warning("Brak połączenia z API GIOŚ — zwracam pustą listę stacji")
        return []
    except Exception:
        logger.exception("Nieoczekiwany błąd przy pobieraniu stacji")
        return []


@router.get("", response_model=Optional[AirQualitySample])
async def jakosc_w_punkcie(
    lat: float = Query(..., description="Szerokość geograficzna"),
    lon: float = Query(..., description="Długość geograficzna"),
    provider: AirQualityProvider = Depends(pobierz_provider_jakosci),
) -> Optional[AirQualitySample]:
    """Zwraca jakość powietrza interpolowaną z najbliższych stacji dla podanego punktu."""
    return await provider.get_air_quality_at(GeoPoint(lat=lat, lon=lon))
