from typing import Dict, List

from ....models.routing import RouteCandidate, RouteRequest, TransportMode
from ..base import RoutingProvider
from .client import OpenRouteServiceHttpClient
from .mapping import mapuj_kandydatow

# Mapowanie TransportMode na profile ORS
PROFILE_ORS: Dict[TransportMode, str] = {
    TransportMode.WALKING: "foot-walking",
    TransportMode.CYCLING: "cycling-regular",
    # Przy rozszerzeniu: TransportMode.DRIVING → "driving-car"
}


class OpenRouteServiceProvider(RoutingProvider):
    """Provider tras oparty o OpenRouteService — obsługuje pieszo i rower, trasy alternatywne."""

    def __init__(self, klient: OpenRouteServiceHttpClient, liczba_alternatyw: int = 3) -> None:
        self.klient = klient
        self.liczba_alternatyw = liczba_alternatyw

    async def get_routes(self, zapytanie: RouteRequest) -> List[RouteCandidate]:
        profil = PROFILE_ORS.get(zapytanie.mode)
        if profil is None:
            raise ValueError(f"Nieobsługiwany tryb transportu: {zapytanie.mode}")

        cialo = {
            "coordinates": [
                [zapytanie.start.lon, zapytanie.start.lat],
                [zapytanie.end.lon, zapytanie.end.lat],
            ],
            "alternative_routes": {
                "target_count": self.liczba_alternatyw,
                # weight_factor i share_factor kontrolują jak bardzo alternatywy mogą się różnić
                "weight_factor": 1.4,
                "share_factor": 0.6,
            },
        }

        odpowiedz = await self.klient.pobierz_trasy(profil, cialo)
        return mapuj_kandydatow(odpowiedz, zapytanie.mode)
