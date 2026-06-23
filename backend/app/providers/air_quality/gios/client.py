from typing import Any

import httpx


class GiosHttpClient:
    """
    Cienkia warstwa HTTP do API GIOŚ.
    GIOŚ nie wymaga klucza API — tylko metoda GET.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._klient = httpx.AsyncClient(timeout=10.0)

    async def pobierz_wszystkie_stacje(self) -> list[dict[str, Any]]:
        odpowiedz = await self._klient.get(f"{self.base_url}/station/findAll")
        odpowiedz.raise_for_status()
        return odpowiedz.json()

    async def pobierz_sensory_stacji(self, id_stacji: int) -> list[dict[str, Any]]:
        odpowiedz = await self._klient.get(f"{self.base_url}/station/sensors/{id_stacji}")
        odpowiedz.raise_for_status()
        return odpowiedz.json()

    async def pobierz_dane_sensora(self, id_sensora: int) -> dict[str, Any]:
        odpowiedz = await self._klient.get(f"{self.base_url}/data/getData/{id_sensora}")
        odpowiedz.raise_for_status()
        return odpowiedz.json()

    async def pobierz_indeks_jakosci(self, id_stacji: int) -> dict[str, Any]:
        odpowiedz = await self._klient.get(f"{self.base_url}/aqindex/getIndex/{id_stacji}")
        odpowiedz.raise_for_status()
        return odpowiedz.json()

    async def zamknij(self) -> None:
        await self._klient.aclose()
