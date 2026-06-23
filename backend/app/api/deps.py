from fastapi import Request

from ..core.optimizer import RouteOptimizer
from ..providers.air_quality.base import AirQualityProvider
from ..providers.routing.base import RoutingProvider


def pobierz_optimizer(request: Request) -> RouteOptimizer:
    return request.app.state.optimizer


def pobierz_provider_jakosci(request: Request) -> AirQualityProvider:
    return request.app.state.provider_jakosci


def pobierz_provider_tras(request: Request) -> RoutingProvider:
    return request.app.state.provider_tras
