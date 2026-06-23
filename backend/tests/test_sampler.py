from app.core.sampler import PollutionSampler
from app.models.air_quality import AirQualitySample
from app.models.routing import RouteCandidate, TransportMode


def _probka(lat: float, lon: float, pm25: float) -> AirQualitySample:
    return AirQualitySample(lat=lat, lon=lon, pm25=pm25, source="test")


def _kandydat_z_geometria(geometria: list) -> RouteCandidate:
    return RouteCandidate(
        geometry=geometria,
        distance_m=1000.0,
        duration_s=600.0,
        mode=TransportMode.WALKING,
    )


def test_oblicza_ekspozycje_dla_prostej_trasy():
    # Krótka trasa w Gdańsku, dwie stacje w pobliżu
    probki = [
        _probka(lat=54.356, lon=18.644, pm25=25.0),
        _probka(lat=54.360, lon=18.650, pm25=30.0),
    ]
    geometria = [[18.644, 54.356], [18.648, 54.358], [18.652, 54.360]]
    kandydat = _kandydat_z_geometria(geometria)

    sampler = PollutionSampler(probki_stacji=probki, co_ile_metrow=100.0)
    profil = sampler.oblicz_ekspozycje(kandydat)

    assert profil.total_exposure > 0
    assert profil.avg_pm25 is not None
    assert profil.peak_pm25 is not None
    assert profil.sample_count > 0


def test_brak_stacji_daje_zerowa_ekspozycje():
    kandydat = _kandydat_z_geometria([[18.644, 54.356], [18.652, 54.360]])
    sampler = PollutionSampler(probki_stacji=[], co_ile_metrow=200.0)
    profil = sampler.oblicz_ekspozycje(kandydat)

    assert profil.total_exposure == 0.0
    assert profil.avg_pm25 is None
    assert profil.peak_pm25 is None


def test_bardziej_zanieczyszczona_trasa_ma_wyzsza_ekspozycje():
    stacja_czysta = [_probka(lat=54.356, lon=18.644, pm25=10.0)]
    stacja_brudna = [_probka(lat=54.356, lon=18.644, pm25=80.0)]
    geometria = [[18.644, 54.356], [18.652, 54.360]]

    sampler_czysty = PollutionSampler(stacja_czysta, co_ile_metrow=100.0)
    sampler_brudny = PollutionSampler(stacja_brudna, co_ile_metrow=100.0)

    kandydat = _kandydat_z_geometria(geometria)
    ekspozycja_czysta = sampler_czysty.oblicz_ekspozycje(kandydat).total_exposure
    ekspozycja_brudna = sampler_brudny.oblicz_ekspozycje(kandydat).total_exposure

    assert ekspozycja_brudna > ekspozycja_czysta
