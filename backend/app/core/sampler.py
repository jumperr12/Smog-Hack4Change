from typing import List, Optional

from ..models.air_quality import AirQualitySample
from ..models.routing import ExposureProfile, ExposureSamplePoint, RouteCandidate
from .geo_utils import haversine, resample_geometrie
from .interpolation import IDWInterpolation


class PollutionSampler:
    """Próbkuje zanieczyszczenie wzdłuż geometrii trasy i oblicza profil ekspozycji."""

    def __init__(self, probki_stacji: List[AirQualitySample], co_ile_metrow: float = 200.0) -> None:
        self.probki_stacji = probki_stacji
        self.co_ile_metrow = co_ile_metrow
        self.interpolacja = IDWInterpolation(k=3)

    def oblicz_ekspozycje(self, kandydat: RouteCandidate) -> ExposureProfile:
        """
        Oblicza ekspozycję na zanieczyszczenie wzdłuż trasy.

        total_exposure = Σ (pm25_i × długość_segmentu_i) [μg/m³·m]
        Jest to proxy ekspozycji — miara kumulatywna, nie bezpośredni wskaźnik zdrowotny.
        """
        punkty_trasy = resample_geometrie(kandydat.geometry, self.co_ile_metrow)

        suma_ekspozycji = 0.0
        suma_pm25 = 0.0
        szczyt_pm25: Optional[float] = None
        punkty_probek: List[ExposureSamplePoint] = []
        licznik_waznych = 0

        for i, punkt in enumerate(punkty_trasy):
            pm25 = self.interpolacja.interpoluj(punkt, self.probki_stacji)

            if pm25 is not None:
                dlugosc_segmentu = (
                    haversine(punkty_trasy[i - 1], punkt) if i > 0 else self.co_ile_metrow
                )
                suma_ekspozycji += pm25 * dlugosc_segmentu
                suma_pm25 += pm25
                licznik_waznych += 1

                if szczyt_pm25 is None or pm25 > szczyt_pm25:
                    szczyt_pm25 = pm25

            punkty_probek.append(ExposureSamplePoint(lat=punkt.lat, lon=punkt.lon, pm25=pm25))

        srednie_pm25 = suma_pm25 / licznik_waznych if licznik_waznych > 0 else None

        return ExposureProfile(
            total_exposure=suma_ekspozycji,
            avg_pm25=srednie_pm25,
            peak_pm25=szczyt_pm25,
            sample_count=len(punkty_trasy),
            samples=punkty_probek,
        )
