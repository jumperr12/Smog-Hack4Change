import logging
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException

from ..core.optimizer import RouteOptimizer
from ..models.routing import RouteRequest, RouteResponse, TransportMode
from .deps import pobierz_optimizer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["trasy"])


@router.get("/transport-modes", response_model=List[str])
async def dostepne_tryby_transportu() -> List[str]:
    """Zwraca listę dostępnych środków transportu. Używane przez frontend do budowania dropdownu."""
    return [tryb.value for tryb in TransportMode]


@router.post("/routes", response_model=RouteResponse)
async def wyznacz_trase(
    zapytanie: RouteRequest,
    optimizer: RouteOptimizer = Depends(pobierz_optimizer),
) -> RouteResponse:
    """
    Wyznacza optymalne trasy z punktu A do B uwzględniając poziom smogu.

    pollution_weight: 0.0 → priorytet czasu, 1.0 → priorytet czystości powietrza.
    Zwraca listę kandydatów z oznaczeniem is_recommended na najlepszej trasie.
    """
    try:
        return await optimizer.optymalizuj(zapytanie)
    except httpx.HTTPStatusError as blad:
        kod = blad.response.status_code
        tresc = blad.response.text[:300]
        logger.error("Błąd HTTP od zewnętrznego API: %s — %s", kod, tresc)
        if kod == 401:
            raise HTTPException(status_code=502, detail="Nieprawidłowy klucz ORS_API_KEY (401)")
        if kod == 403:
            raise HTTPException(status_code=502, detail="Brak dostępu do ORS API (403) — sprawdź klucz")
        if kod == 429:
            raise HTTPException(status_code=502, detail="Przekroczono limit zapytań ORS (429)")
        raise HTTPException(status_code=502, detail=f"Błąd zewnętrznego API ({kod}): {tresc}")
    except httpx.ConnectError:
        logger.error("Brak połączenia z ORS API")
        raise HTTPException(status_code=502, detail="Nie można połączyć się z ORS API — sprawdź internet")
    except Exception as blad:
        logger.exception("Nieoczekiwany błąd podczas wyznaczania trasy")
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {blad}")
