from typing import List, Optional

from ....cache import TTLCache
from ....config import settings
from ....models.air_quality import AirQualitySample, Station
from ....models.geo import BBox, GeoPoint
from ..base import AirQualityProvider
from .client import OpenMeteoHttpClient
from .mapping import mapuj_probke


def _zbuduj_siatke(bbox: BBox, krok_stopnie: float, max_na_os: int) -> List[GeoPoint]:
    """
    Buduje równomierną siatkę punktów wewnątrz bboxa.
    Gęstość ograniczona do max_na_os na każdą oś — gęstsza siatka niż rozdzielczość
    modelu (~11 km) nic nie wnosi, a zwiększa rozmiar żądania.
    """
    def os_wartosci(minimum: float, maksimum: float) -> List[float]:
        rozpietosc = maksimum - minimum
        if rozpietosc <= 0:
            return [minimum]
        liczba_krokow = min(int(rozpietosc / krok_stopnie), max_na_os - 1)
        if liczba_krokow < 1:
            return [minimum, maksimum]
        return [minimum + i * rozpietosc / liczba_krokow for i in range(liczba_krokow + 1)]

    szerokosci = os_wartosci(bbox.min_lat, bbox.max_lat)
    dlugosci = os_wartosci(bbox.min_lon, bbox.max_lon)

    return [GeoPoint(lat=lat, lon=lon) for lat in szerokosci for lon in dlugosci]


class OpenMeteoAirQualityProvider(AirQualityProvider):
    """
    Provider jakości powietrza oparty o model Open-Meteo (CAMS, ~11 km).
    W przeciwieństwie do GIOŚ zwraca wartość dla dowolnego punktu — pokrywa
    również obszary bez stacji pomiarowych (Półwysep Helski, otwarte tereny).
    """

    MARGINES_STOPNIE = 0.05
    KROK_SIATKI_STOPNIE = 0.05   # ~5.5 km
    MAX_PUNKTOW_NA_OS = 6

    def __init__(self, klient: OpenMeteoHttpClient, cache: TTLCache) -> None:
        self.klient = klient
        self.cache = cache

    async def get_stations(self, bbox: BBox) -> List[Station]:
        # Open-Meteo to model siatkowy — brak fizycznych stacji do pokazania na mapie
        return []

    async def get_air_quality_at(self, punkt: GeoPoint) -> Optional[AirQualitySample]:
        klucz = f"om:{punkt.lat:.2f},{punkt.lon:.2f}"
        zapisana = self.cache.get(klucz)
        if zapisana is not None:
            return zapisana

        odpowiedzi = await self.klient.pobierz_jakosc([punkt])
        if not odpowiedzi:
            return None

        probka = mapuj_probke(odpowiedzi[0])
        if probka is not None:
            self.cache.set(klucz, probka, settings.cache_ttl_pomiary)
        return probka

    async def get_samples_near(self, punkt_a: GeoPoint, punkt_b: GeoPoint) -> List[AirQualitySample]:
        """Buduje siatkę punktów wokół odcinka A–B i pobiera dla nich model jednym żądaniem."""
        bbox = BBox(
            min_lat=min(punkt_a.lat, punkt_b.lat) - self.MARGINES_STOPNIE,
            min_lon=min(punkt_a.lon, punkt_b.lon) - self.MARGINES_STOPNIE,
            max_lat=max(punkt_a.lat, punkt_b.lat) + self.MARGINES_STOPNIE,
            max_lon=max(punkt_a.lon, punkt_b.lon) + self.MARGINES_STOPNIE,
        )

        klucz = (
            f"om-siatka:{bbox.min_lat:.2f},{bbox.min_lon:.2f},"
            f"{bbox.max_lat:.2f},{bbox.max_lon:.2f}"
        )
        zapisane = self.cache.get(klucz)
        if zapisane is not None:
            return zapisane

        siatka = _zbuduj_siatke(bbox, self.KROK_SIATKI_STOPNIE, self.MAX_PUNKTOW_NA_OS)
        odpowiedzi = await self.klient.pobierz_jakosc(siatka)
        probki = [p for p in (mapuj_probke(o) for o in odpowiedzi) if p is not None]

        self.cache.set(klucz, probki, settings.cache_ttl_pomiary)
        return probki
