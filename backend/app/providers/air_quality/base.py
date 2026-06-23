from abc import ABC, abstractmethod
from typing import List

from ...models.air_quality import AirQualitySample, Station
from ...models.geo import BBox, GeoPoint


class AirQualityProvider(ABC):
    """
    Interfejs dostawcy danych o jakości powietrza.

    Aby dodać nowe źródło (Airly, OpenAQ itp.) wystarczy:
    1. Stworzyć podklasę implementującą poniższe metody
    2. Zarejestrować ją w providers/registry.py
    3. Ustawić nazwę w konfiguracji (air_quality_provider)
    """

    @abstractmethod
    async def get_stations(self, bbox: BBox) -> List[Station]:
        """Zwraca stacje pomiarowe wewnątrz prostokąta ograniczającego."""
        ...

    @abstractmethod
    async def get_air_quality_at(self, punkt: GeoPoint) -> AirQualitySample | None:
        """Zwraca jakość powietrza w podanym punkcie (interpolowana lub z najbliższej stacji)."""
        ...

    @abstractmethod
    async def get_samples_near(self, punkt_a: GeoPoint, punkt_b: GeoPoint) -> List[AirQualitySample]:
        """Zwraca próbki ze stacji w pobliżu odcinka A–B (używane przez PollutionSampler)."""
        ...
