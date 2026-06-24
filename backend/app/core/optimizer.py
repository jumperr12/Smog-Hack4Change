import asyncio
from typing import List

from ..models.routing import RouteCandidate, RouteRequest, RouteResponse
from ..providers.air_quality.base import AirQualityProvider
from ..providers.routing.base import RoutingProvider
from .cost import LinearCostFunction
from .sampler import PollutionSampler


class RouteOptimizer:
    """
    Orkiestruje cały proces optymalizacji:
    1. Pobiera trasy alternatywne od providera
    2. Pobiera próbki smogu w okolicy trasy
    3. Dla każdej trasy próbkuje ekspozycję (równolegle)
    4. Oblicza koszt i wskazuje rekomendowaną trasę
    """

    def __init__(
        self,
        provider_jakosci: AirQualityProvider,
        provider_tras: RoutingProvider,
    ) -> None:
        self.provider_jakosci = provider_jakosci
        self.provider_tras = provider_tras
        self.funkcja_kosztu = LinearCostFunction()

    async def optymalizuj(self, zapytanie: RouteRequest) -> RouteResponse:
        kandydaci: List[RouteCandidate] = await self.provider_tras.get_routes(zapytanie)

        if not kandydaci:
            return RouteResponse(request=zapytanie, candidates=[], recommended_index=None)

        try:
            probki = await self.provider_jakosci.get_samples_near(zapytanie.start, zapytanie.end)
        except Exception:
            # Gdy GIOŚ jest niedostępny — trasy zwracamy bez danych o smogu
            probki = []

        sampler = PollutionSampler(
            probki_stacji=probki,
            co_ile_metrow=200.0,
        )

        # Próbkowanie ekspozycji dla każdej trasy — uruchamiane równolegle w wątkach
        # (obliczenia CPU-bound, nie blokują pętli zdarzeń)
        ekspozycje = await asyncio.gather(
            *[asyncio.to_thread(sampler.oblicz_ekspozycje, k) for k in kandydaci]
        )

        for kandydat, ekspozycja in zip(kandydaci, ekspozycje):
            kandydat.exposure = ekspozycja

        koszty = self.funkcja_kosztu.oblicz(kandydaci, zapytanie.pollution_weight)
        indeks_najlepszej = koszty.index(min(koszty))

        for i, (kandydat, koszt) in enumerate(zip(kandydaci, koszty)):
            kandydat.cost = round(koszt, 4)
            kandydat.is_recommended = i == indeks_najlepszej

        return RouteResponse(
            request=zapytanie,
            candidates=kandydaci,
            recommended_index=indeks_najlepszej,
        )
