from typing import List

from ..models.routing import RouteCandidate


class LinearCostFunction:
    """
    Koszt trasy jako liniowa kombinacja znormalizowanej ekspozycji i czasu.

    koszt = waga × ekspozycja_norm + (1 − waga) × czas_norm

    Im niższy koszt, tym lepiej.
    waga = 0  →  wybiera najszybszą trasę
    waga = 1  →  wybiera trasę z najniższą ekspozycją na smog
    """

    def oblicz(self, kandydaci: List[RouteCandidate], waga_zanieczyszczenia: float) -> List[float]:
        ekspozycje = [
            k.exposure.total_exposure if k.exposure is not None else 0.0
            for k in kandydaci
        ]
        czasy = [k.duration_s for k in kandydaci]

        koszty = []
        for ekspozycja, czas in zip(ekspozycje, czasy):
            ekspozycja_norm = self._normalizuj(ekspozycja, ekspozycje)
            czas_norm = self._normalizuj(czas, czasy)
            koszt = waga_zanieczyszczenia * ekspozycja_norm + (1 - waga_zanieczyszczenia) * czas_norm
            koszty.append(koszt)

        return koszty

    def _normalizuj(self, wartosc: float, wszystkie: List[float]) -> float:
        """Min-max normalizacja do zakresu [0, 1]."""
        minimum = min(wszystkie)
        maksimum = max(wszystkie)
        if maksimum == minimum:
            return 0.0
        return (wartosc - minimum) / (maksimum - minimum)
