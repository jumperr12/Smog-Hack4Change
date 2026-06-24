from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # OpenRouteService
    ors_api_key: str = ""
    ors_alternative_routes_count: int = 3

    # GIOŚ — base URL konfigurowalne żeby łatwo przejść z /rest na /v1/rest gdy stara wersja zostanie wyłączona
    gios_base_url: str = "https://api.gios.gov.pl/pjp-api/v1/rest"

    # TTL cache w sekundach
    cache_ttl_stacje: int = 86_400   # 24h — stacje rzadko się zmieniają
    cache_ttl_pomiary: int = 3_600   # 1h — pomiary odświeżane co godzinę

    # Domyślny obszar Trójmiasta (Gdańsk / Gdynia / Sopot)
    # Zmień wartości żeby obsługiwać inne miasto
    bbox_min_lat: float = 54.25
    bbox_min_lon: float = 18.40
    bbox_max_lat: float = 54.60
    bbox_max_lon: float = 18.80

    # Nazwy aktywnych providerów — zmień żeby podłączyć Airly, GraphHopper itp.
    air_quality_provider: str = "gios"
    routing_provider: str = "openrouteservice"

    # Co ile metrów próbkować smog wzdłuż trasy
    sampling_interval_m: float = 200.0


settings = Settings()
