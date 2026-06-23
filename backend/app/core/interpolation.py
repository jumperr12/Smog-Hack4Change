from typing import List, Optional

from ..models.air_quality import AirQualitySample
from ..models.geo import GeoPoint
from .geo_utils import haversine


class NearestStationInterpolation:
    """Zwraca wartość PM2.5 z najbliższej stacji posiadającej dane."""

    def interpoluj(self, punkt: GeoPoint, probki: List[AirQualitySample]) -> Optional[float]:
        probki_z_pm25 = [p for p in probki if p.pm25 is not None]
        if not probki_z_pm25:
            return None

        najblizszy = min(
            probki_z_pm25,
            key=lambda p: haversine(punkt, GeoPoint(lat=p.lat, lon=p.lon)),
        )
        return najblizszy.pm25


class IDWInterpolation:
    """
    Inverse Distance Weighting — ważona odległością średnia z k najbliższych stacji.
    Lepiej radzi sobie z rzadką siecią stacji GIOŚ niż prosty nearest-neighbor.
    """

    def __init__(self, k: int = 3, potega: float = 2.0) -> None:
        self.k = k
        self.potega = potega

    def interpoluj(self, punkt: GeoPoint, probki: List[AirQualitySample]) -> Optional[float]:
        probki_z_pm25 = [p for p in probki if p.pm25 is not None]
        if not probki_z_pm25:
            return None

        posortowane = sorted(
            probki_z_pm25,
            key=lambda p: haversine(punkt, GeoPoint(lat=p.lat, lon=p.lon)),
        )
        kandydaci = posortowane[: self.k]

        licznik = 0.0
        mianownik = 0.0

        for probka in kandydaci:
            odleglosc = haversine(punkt, GeoPoint(lat=probka.lat, lon=probka.lon))
            if odleglosc < 1:
                # Trafiliśmy dokładnie na stację — zwróć jej wartość bez ważenia
                return probka.pm25
            waga = 1.0 / (odleglosc ** self.potega)
            licznik += waga * probka.pm25  # type: ignore[operator]
            mianownik += waga

        return licznik / mianownik if mianownik > 0 else None
