from app.core.cost import LinearCostFunction
from app.models.routing import ExposureProfile, RouteCandidate, TransportMode


def _kandydat(czas: float, ekspozycja: float) -> RouteCandidate:
    profil = ExposureProfile(
        total_exposure=ekspozycja,
        avg_pm25=None,
        peak_pm25=None,
        sample_count=0,
        samples=[],
    )
    return RouteCandidate(
        geometry=[],
        distance_m=1000.0,
        duration_s=czas,
        mode=TransportMode.WALKING,
        exposure=profil,
    )


def test_waga_1_preferuje_najczystsza():
    kandydaci = [
        _kandydat(czas=600, ekspozycja=5_000),    # czysta, trochę wolniejsza
        _kandydat(czas=600, ekspozycja=50_000),   # brudna
    ]
    funkcja = LinearCostFunction()
    koszty = funkcja.oblicz(kandydaci, waga_zanieczyszczenia=1.0)
    assert koszty[0] < koszty[1]


def test_waga_0_preferuje_najszybsza():
    kandydaci = [
        _kandydat(czas=300, ekspozycja=50_000),   # szybka, ale brudna
        _kandydat(czas=900, ekspozycja=1_000),    # wolna, ale czysta
    ]
    funkcja = LinearCostFunction()
    koszty = funkcja.oblicz(kandydaci, waga_zanieczyszczenia=0.0)
    assert koszty[0] < koszty[1]


def test_identyczne_trasy_maja_zerowy_koszt():
    kandydaci = [
        _kandydat(czas=600, ekspozycja=5_000),
        _kandydat(czas=600, ekspozycja=5_000),
    ]
    funkcja = LinearCostFunction()
    koszty = funkcja.oblicz(kandydaci, waga_zanieczyszczenia=0.5)
    assert koszty[0] == 0.0
    assert koszty[1] == 0.0


def test_wyniki_sa_w_zakresie_0_1():
    kandydaci = [
        _kandydat(czas=300, ekspozycja=1_000),
        _kandydat(czas=600, ekspozycja=10_000),
        _kandydat(czas=900, ekspozycja=50_000),
    ]
    funkcja = LinearCostFunction()
    koszty = funkcja.oblicz(kandydaci, waga_zanieczyszczenia=0.5)
    for koszt in koszty:
        assert 0.0 <= koszt <= 1.0
