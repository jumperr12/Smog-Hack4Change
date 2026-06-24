import asyncio
from typing import List, Optional

from ....cache import TTLCache
from ....config import settings
from ....core.geo_utils import haversine, punkt_w_bbox
from ....models.air_quality import AirQualitySample, Station
from ....models.geo import BBox, GeoPoint
from ..base import AirQualityProvider
from .client import GiosHttpClient
from .mapping import _wyciagnij_liste, znajdz_sensor_pm, mapuj_probke, mapuj_stacje


class GiosAirQualityProvider(AirQualityProvider):
    """
    Provider danych o jakości powietrza oparty o API GIOŚ (v1/rest).
    Oficjalne polskie API — bez klucza, bezpłatne.
    """

    def __init__(self, klient: GiosHttpClient, cache: TTLCache) -> None:
        self.klient = klient
        self.cache = cache

    async def get_stations(self, bbox: BBox) -> List[Station]:
        klucz = f"stacje:{bbox.min_lat},{bbox.min_lon},{bbox.max_lat},{bbox.max_lon}"
        zapisane = self.cache.get(klucz)
        if zapisane is not None:
            return zapisane

        odpowiedz = await self.klient.pobierz_wszystkie_stacje()
        lista_surowa = _wyciagnij_liste(odpowiedz)
        wszystkie_stacje = [mapuj_stacje(s) for s in lista_surowa]

        stacje_w_obszarze = [
            s for s in wszystkie_stacje
            if s is not None and punkt_w_bbox(GeoPoint(lat=s.lat, lon=s.lon), bbox)
        ]

        self.cache.set(klucz, stacje_w_obszarze, settings.cache_ttl_stacje)
        return stacje_w_obszarze

    async def _pobierz_probke_dla_stacji(self, stacja: Station) -> Optional[AirQualitySample]:
        """Pobiera aktualny pomiar PM2.5/PM10 dla jednej stacji. Wynik trafia do cache."""
        klucz = f"probka:{stacja.id}"
        zapisana = self.cache.get(klucz)
        if zapisana is not None:
            return zapisana

        try:
            odpowiedz_sensorow = await self.klient.pobierz_sensory_stacji(stacja.id)
            wynik_sensora = znajdz_sensor_pm(odpowiedz_sensorow)
            if wynik_sensora is None:
                return None

            id_sensora, czy_pm25 = wynik_sensora
            dane = await self.klient.pobierz_dane_sensora(id_sensora)
            probka = mapuj_probke(stacja, dane, czy_pm25)

            if probka is not None:
                self.cache.set(klucz, probka, settings.cache_ttl_pomiary)
            return probka
        except Exception:
            return None

    async def get_air_quality_at(self, punkt: GeoPoint) -> Optional[AirQualitySample]:
        bbox_trojmiasta = BBox(
            min_lat=settings.bbox_min_lat,
            min_lon=settings.bbox_min_lon,
            max_lat=settings.bbox_max_lat,
            max_lon=settings.bbox_max_lon,
        )
        stacje = await self.get_stations(bbox_trojmiasta)
        probki_raw = await asyncio.gather(*[self._pobierz_probke_dla_stacji(s) for s in stacje])
        probki = [p for p in probki_raw if p is not None]

        if not probki:
            return None

        return min(probki, key=lambda p: haversine(punkt, GeoPoint(lat=p.lat, lon=p.lon)))

    async def get_samples_near(self, punkt_a: GeoPoint, punkt_b: GeoPoint) -> List[AirQualitySample]:
        """Pobiera próbki ze stacji w obszarze wokół odcinka A–B z marginesem 0.1°."""
        margines = 0.1
        bbox = BBox(
            min_lat=min(punkt_a.lat, punkt_b.lat) - margines,
            min_lon=min(punkt_a.lon, punkt_b.lon) - margines,
            max_lat=max(punkt_a.lat, punkt_b.lat) + margines,
            max_lon=max(punkt_a.lon, punkt_b.lon) + margines,
        )
        stacje = await self.get_stations(bbox)
        probki_raw = await asyncio.gather(*[self._pobierz_probke_dla_stacji(s) for s in stacje])
        return [p for p in probki_raw if p is not None]
