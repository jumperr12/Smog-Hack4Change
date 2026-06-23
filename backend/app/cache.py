import time
from typing import Any, Optional


class TTLCache:
    """Prosty cache in-memory z czasem wygasania wpisów."""

    def __init__(self) -> None:
        self._dane: dict[str, tuple[Any, float]] = {}

    def get(self, klucz: str) -> Optional[Any]:
        wpis = self._dane.get(klucz)
        if wpis is None:
            return None
        wartosc, czas_wygasniecia = wpis
        if time.monotonic() > czas_wygasniecia:
            del self._dane[klucz]
            return None
        return wartosc

    def set(self, klucz: str, wartosc: Any, ttl_s: float) -> None:
        czas_wygasniecia = time.monotonic() + ttl_s
        self._dane[klucz] = (wartosc, czas_wygasniecia)

    def clear(self) -> None:
        self._dane.clear()
