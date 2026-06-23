import pytest

from app.core.optimizer import RouteOptimizer
from app.models.air_quality import AirQualitySample
from app.models.geo import GeoPoint
from app.models.routing import RouteCandidate, RouteRequest, TransportMode


class MockAirQualityProvider:
    """Zaślepka providera jakości powietrza — zwraca predefiniowane próbki bez sieci."""

    def __init__(self, probki: list[AirQualitySample]) -> None:
        self.probki = probki

    async def get_stations(self, bbox):
        return []

    async def get_air_quality_at(self, punkt):
        return self.probki[0] if self.probki else None

    async def get_samples_near(self, punkt_a, punkt_b):
        return self.probki


class MockRoutingProvider:
    """Zaślepka providera tras — zwraca predefiniowane kandydatów bez sieci."""

    def __init__(self, kandydaci: list[RouteCandidate]) -> None:
        self.kandydaci = kandydaci

    async def get_routes(self, zapytanie):
        return self.kandydaci


def _probka_pm25(pm25: float) -> AirQualitySample:
    return AirQualitySample(lat=54.36, lon=18.64, pm25=pm25, source="test")


def _kandydat(czas: float, geometria: list | None = None) -> RouteCandidate:
    return RouteCandidate(
        geometry=geometria or [[18.644, 54.356], [18.652, 54.360]],
        distance_m=1000.0,
        duration_s=czas,
        mode=TransportMode.WALKING,
    )


@pytest.mark.asyncio
async def test_optymalizator_oznacza_rekomendowana():
    probki = [_probka_pm25(20.0)]
    kandydaci = [_kandydat(300.0), _kandydat(600.0), _kandydat(900.0)]

    optimizer = RouteOptimizer(
        provider_jakosci=MockAirQualityProvider(probki),
        provider_tras=MockRoutingProvider(kandydaci),
    )
    zapytanie = RouteRequest(
        start=GeoPoint(lat=54.356, lon=18.644),
        end=GeoPoint(lat=54.360, lon=18.652),
        mode=TransportMode.WALKING,
        pollution_weight=0.5,
    )
    odpowiedz = await optimizer.optymalizuj(zapytanie)

    assert len(odpowiedz.candidates) == 3
    assert odpowiedz.recommended_index is not None
    rekomendowane = [k for k in odpowiedz.candidates if k.is_recommended]
    assert len(rekomendowane) == 1


@pytest.mark.asyncio
async def test_optymalizator_brak_tras_zwraca_pusta_liste():
    optimizer = RouteOptimizer(
        provider_jakosci=MockAirQualityProvider([]),
        provider_tras=MockRoutingProvider([]),
    )
    zapytanie = RouteRequest(
        start=GeoPoint(lat=54.356, lon=18.644),
        end=GeoPoint(lat=54.360, lon=18.652),
        mode=TransportMode.WALKING,
    )
    odpowiedz = await optimizer.optymalizuj(zapytanie)

    assert odpowiedz.candidates == []
    assert odpowiedz.recommended_index is None


@pytest.mark.asyncio
async def test_waga_0_preferuje_najszybsza():
    probki = [_probka_pm25(50.0)]
    # Trasa szybka i brudna, trasa wolna i czysta
    kandydaci = [
        _kandydat(czas=300.0, geometria=[[18.644, 54.356], [18.645, 54.357]]),
        _kandydat(czas=900.0, geometria=[[18.644, 54.356], [18.652, 54.365]]),
    ]

    optimizer = RouteOptimizer(
        provider_jakosci=MockAirQualityProvider(probki),
        provider_tras=MockRoutingProvider(kandydaci),
    )
    zapytanie = RouteRequest(
        start=GeoPoint(lat=54.356, lon=18.644),
        end=GeoPoint(lat=54.360, lon=18.652),
        mode=TransportMode.WALKING,
        pollution_weight=0.0,  # tylko czas
    )
    odpowiedz = await optimizer.optymalizuj(zapytanie)

    assert odpowiedz.candidates[0].is_recommended is True  # najszybsza to pierwsza
