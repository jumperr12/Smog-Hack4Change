from typing import Any

import httpx


class OpenRouteServiceHttpClient:
    """Klient HTTP do OpenRouteService API. Wymaga klucza API przekazywanego w nagłówku Authorization."""

    BASE_URL = "https://api.openrouteservice.org"

    def __init__(self, klucz_api: str) -> None:
        self._klient = httpx.AsyncClient(
            timeout=15.0,
            headers={
                "Authorization": klucz_api,
                "Content-Type": "application/json",
            },
        )

    async def pobierz_trasy(self, profil: str, cialo: dict[str, Any]) -> dict[str, Any]:
        """POST /v2/directions/{profil}/geojson — zwraca FeatureCollection z trasami."""
        url = f"{self.BASE_URL}/v2/directions/{profil}/geojson"
        odpowiedz = await self._klient.post(url, json=cialo)
        odpowiedz.raise_for_status()
        return odpowiedz.json()

    async def zamknij(self) -> None:
        await self._klient.aclose()
