from ..cache import TTLCache
from ..config import settings
from .air_quality.base import AirQualityProvider
from .air_quality.gios.client import GiosHttpClient
from .air_quality.gios.provider import GiosAirQualityProvider
from .routing.base import RoutingProvider
from .routing.openrouteservice.client import OpenRouteServiceHttpClient
from .routing.openrouteservice.provider import OpenRouteServiceProvider

# Jeden wspólny cache na czas życia procesu
_cache = TTLCache()


def zbuduj_provider_jakosci() -> AirQualityProvider:
    """
    Tworzy provider jakości powietrza na podstawie ustawienia air_quality_provider.
    Aby dodać nowy provider: dodaj warunek if i zarejestruj klasę.
    """
    nazwa = settings.air_quality_provider

    if nazwa == "gios":
        klient = GiosHttpClient(settings.gios_base_url)
        return GiosAirQualityProvider(klient, _cache)

    raise ValueError(
        f"Nieznany provider jakości powietrza: '{nazwa}'. "
        f"Dostępne: 'gios'"
    )


def zbuduj_provider_tras() -> RoutingProvider:
    """
    Tworzy provider tras na podstawie ustawienia routing_provider.
    Aby dodać nowy provider: dodaj warunek if i zarejestruj klasę.
    """
    nazwa = settings.routing_provider

    if nazwa == "openrouteservice":
        klient = OpenRouteServiceHttpClient(settings.ors_api_key)
        return OpenRouteServiceProvider(klient, settings.ors_alternative_routes_count)

    raise ValueError(
        f"Nieznany provider tras: '{nazwa}'. "
        f"Dostępne: 'openrouteservice'"
    )
