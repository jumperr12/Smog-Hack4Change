from typing import Any

import httpx

# Nowe API GIOŚ wymaga parametru size (paginacja obowiązkowa)
ROZMIAR_STRONY_STACJE = 500   # jest ~300 stacji w Polsce, mieści się w jednym żądaniu
ROZMIAR_STRONY_POMIARY = 25   # ostatnie 25 godzin wystarczy do wyznaczenia aktualnej wartości


class GiosHttpClient:
    """
    Warstwa HTTP do API GIOŚ (v1/rest).
    GIOŚ nie wymaga klucza API — tylko metoda GET.
    Nowe API wymaga parametru size przy każdym żądaniu listującym.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._klient = httpx.AsyncClient(timeout=15.0)

    async def pobierz_wszystkie_stacje(self) -> dict[str, Any]:
        """Zwraca słownik z listą stacji i metadanymi paginacji."""
        odpowiedz = await self._klient.get(
            f"{self.base_url}/station/findAll",
            params={"size": ROZMIAR_STRONY_STACJE},
        )
        odpowiedz.raise_for_status()
        return odpowiedz.json()

    async def pobierz_sensory_stacji(self, id_stacji: int) -> dict[str, Any]:
        """Zwraca słownik z listą sensorów dla danej stacji."""
        odpowiedz = await self._klient.get(
            f"{self.base_url}/station/sensors/{id_stacji}",
            params={"size": 50},
        )
        odpowiedz.raise_for_status()
        return odpowiedz.json()

    async def pobierz_dane_sensora(self, id_sensora: int) -> dict[str, Any]:
        """Zwraca ostatnie pomiary dla sensora (Lista danych pomiarowych)."""
        odpowiedz = await self._klient.get(
            f"{self.base_url}/data/getData/{id_sensora}",
            params={"size": ROZMIAR_STRONY_POMIARY},
        )
        odpowiedz.raise_for_status()
        return odpowiedz.json()

    async def zamknij(self) -> None:
        await self._klient.aclose()
