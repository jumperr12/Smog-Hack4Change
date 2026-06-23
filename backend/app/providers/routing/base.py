from abc import ABC, abstractmethod
from typing import List

from ...models.routing import RouteCandidate, RouteRequest


class RoutingProvider(ABC):
    """
    Interfejs dostawcy wyznaczania tras.

    Aby dodać nowe źródło (GraphHopper, OSRM itp.) wystarczy:
    1. Stworzyć podklasę implementującą get_routes
    2. Zarejestrować ją w providers/registry.py
    3. Ustawić nazwę w konfiguracji (routing_provider)
    """

    @abstractmethod
    async def get_routes(self, zapytanie: RouteRequest) -> List[RouteCandidate]:
        """Zwraca listę kandydatów tras dla podanego zapytania (bez wypełnionej ekspozycji)."""
        ...
