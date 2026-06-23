from datetime import datetime
from typing import Any, Optional

from ....models.air_quality import AirQualitySample, Station


def mapuj_stacje(surowe: dict[str, Any]) -> Optional[Station]:
    """Mapuje surową odpowiedź GIOŚ na model Station. Zwraca None jeśli brakuje wymaganych pól."""
    try:
        miasto = surowe.get("city") or {}
        nazwa_miasta = miasto.get("name", "") if isinstance(miasto, dict) else ""
        return Station(
            id=surowe["id"],
            name=surowe.get("stationName", ""),
            lat=float(surowe["gegrLat"]),
            lon=float(surowe["gegrLon"]),
            city=nazwa_miasta,
        )
    except (KeyError, ValueError, TypeError):
        return None


def znajdz_sensor_pm(sensory: list[dict[str, Any]]) -> Optional[int]:
    """
    Szuka sensora PM2.5, fallback na PM10.
    Zwraca id sensora lub None jeśli nie ma żadnego z tych parametrów.
    """
    id_sensora_pm10 = None

    for sensor in sensory:
        param = sensor.get("param", {})
        kod = (param.get("paramFormula") or param.get("paramCode") or "").upper()

        if "PM2.5" in kod or "PM25" in kod:
            return sensor["id"]
        if "PM10" in kod and id_sensora_pm10 is None:
            id_sensora_pm10 = sensor["id"]

    return id_sensora_pm10


def mapuj_probke(stacja: Station, dane: dict[str, Any]) -> Optional[AirQualitySample]:
    """
    Wyciąga ostatni ważny pomiar z danych sensora.
    Pierwsze niepuste value w liście values traktuje jako aktualne.
    """
    klucz_parametru = (dane.get("key") or "").upper()
    wartosci = dane.get("values", [])

    for wpis in wartosci:
        if wpis.get("value") is None:
            continue

        pm25 = None
        pm10 = None

        if "PM2.5" in klucz_parametru or "PM25" in klucz_parametru:
            pm25 = float(wpis["value"])
        elif "PM10" in klucz_parametru:
            pm10 = float(wpis["value"])
        else:
            # Nieznany parametr — pomiń
            continue

        timestamp = None
        if wpis.get("date"):
            try:
                timestamp = datetime.fromisoformat(wpis["date"])
            except ValueError:
                pass

        return AirQualitySample(
            lat=stacja.lat,
            lon=stacja.lon,
            pm25=pm25,
            pm10=pm10,
            source="gios",
            timestamp=timestamp,
        )

    return None
