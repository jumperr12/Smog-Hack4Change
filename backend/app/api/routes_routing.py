from typing import List

from fastapi import APIRouter, Depends

from ..core.optimizer import RouteOptimizer
from ..models.routing import RouteRequest, RouteResponse, TransportMode
from .deps import pobierz_optimizer

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
    return await optimizer.optymalizuj(zapytanie)
