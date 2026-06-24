import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes_air import router as router_jakosci
from .api.routes_routing import router as router_tras
from .api.ws import router as router_ws
from .config import settings
from .core.optimizer import RouteOptimizer
from .providers.registry import zbuduj_provider_jakosci, zbuduj_provider_tras

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Inicjalizacja providerów i optymalizatora przy starcie serwera
    if not settings.ors_api_key:
        logger.warning("ORS_API_KEY jest pusty — wyznaczanie tras nie będzie działać")

    app.state.provider_jakosci = zbuduj_provider_jakosci()
    app.state.provider_tras = zbuduj_provider_tras()
    app.state.optimizer = RouteOptimizer(
        provider_jakosci=app.state.provider_jakosci,
        provider_tras=app.state.provider_tras,
    )

    yield

    # Sprzątanie — zamknięcie klientów HTTP przy zatrzymaniu serwera
    await app.state.provider_jakosci.klient.zamknij()
    await app.state.provider_tras.klient.zamknij()


app = FastAPI(
    title="Smog Route Optimizer",
    description="API do wyznaczania tras z uwzględnieniem zanieczyszczenia powietrza.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # adres Vite dev serwera
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_jakosci)
app.include_router(router_tras)
app.include_router(router_ws)


@app.get("/health", tags=["meta"])
async def health_check() -> dict:
    """Endpoint do sprawdzenia czy serwer działa."""
    return {"status": "ok"}
