from typing import Any

import httpx

from ....models.geo import GeoPoint


class OpenMeteoHttpClient:
    """
    Warstwa HTTP do API Open-Meteo Air Quality.
    Model CAMS (~11 km) — nie wymaga klucza, zwraca wartość dla dowolnego punktu.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._klient = httpx.AsyncClient(timeout=15.0)

    async def pobierz_jakosc(self, punkty: list[GeoPoint]) -> list[dict[str, Any]]:
        """
        Pobiera aktualne PM2.5/PM10 dla listy punktów w jednym żądaniu.
        Open-Meteo zwraca obiekt dla jednego punktu, a tablicę dla wielu — normalizujemy do listy.
        """
        if not punkty:
            return []

        szerokosci = ",".join(f"{p.lat:.5f}" for p in punkty)
        dlugosci = ",".join(f"{p.lon:.5f}" for p in punkty)

        odpowiedz = await self._klient.get(
            self.base_url,
            params={
                "latitude": szerokosci,
                "longitude": dlugosci,
                "current": "pm2_5,pm10",
            },
        )
        odpowiedz.raise_for_status()
        dane = odpowiedz.json()

        # Jeden punkt → pojedynczy obiekt, wiele punktów → tablica obiektów
        if isinstance(dane, list):
            return dane
        return [dane]

    async def zamknij(self) -> None:
        await self._klient.aclose()
