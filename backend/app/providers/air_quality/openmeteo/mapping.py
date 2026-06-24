from datetime import datetime
from typing import Any, Optional

from ....models.air_quality import AirQualitySample


def mapuj_probke(surowe: dict[str, Any]) -> Optional[AirQualitySample]:
    """
    Mapuje pojedynczy obiekt lokalizacji z odpowiedzi Open-Meteo na AirQualitySample.
    Wartości pochodzą z modelu CAMS (nie z fizycznej stacji), więc lat/lon są
    przyciągnięte do siatki modelu — to oczekiwane.
    """
    biezace = surowe.get("current")
    if not biezace:
        return None

    try:
        lat = float(surowe["latitude"])
        lon = float(surowe["longitude"])
    except (KeyError, ValueError, TypeError):
        return None

    pm25 = biezace.get("pm2_5")
    pm10 = biezace.get("pm10")
    if pm25 is None and pm10 is None:
        return None

    timestamp = None
    if biezace.get("time"):
        try:
            timestamp = datetime.fromisoformat(biezace["time"])
        except ValueError:
            pass

    return AirQualitySample(
        lat=lat,
        lon=lon,
        pm25=float(pm25) if pm25 is not None else None,
        pm10=float(pm10) if pm10 is not None else None,
        source="openmeteo",
        timestamp=timestamp,
    )
