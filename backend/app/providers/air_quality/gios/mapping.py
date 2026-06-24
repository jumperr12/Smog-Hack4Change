from datetime import datetime
from typing import Any, Optional

from ....models.air_quality import AirQualitySample, Station


def _wyciagnij_liste(odpowiedz: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Nowe API GIOŚ zwraca listy w kluczu zaczynającym się od 'Lista'.
    Szukamy pierwszego klucza, którego wartość jest listą słowników.
    """
    for wartosc in odpowiedz.values():
        if isinstance(wartosc, list) and wartosc and isinstance(wartosc[0], dict):
            return wartosc
    return []


def mapuj_stacje(surowe: dict[str, Any]) -> Optional[Station]:
    """
    Mapuje surowy wpis stacji z nowego API GIOŚ (v1/rest) na model Station.
    Nowe API używa polskich nazw pól zamiast angielskich.
    """
    try:
        return Station(
            id=surowe["Identyfikator stacji"],
            name=surowe.get("Nazwa stacji", ""),
            lat=float(surowe["WGS84 φ N"]),
            lon=float(surowe["WGS84 λ E"]),
            city=surowe.get("Nazwa miasta", ""),
        )
    except (KeyError, ValueError, TypeError):
        return None


def znajdz_sensor_pm(odpowiedz: dict[str, Any]) -> Optional[tuple[int, bool]]:
    """
    Szuka sensora PM2.5 (priorytet) lub PM10 (fallback) w odpowiedzi sensorów stacji.
    Zwraca krotkę (id_sensora, czy_pm25) lub None jeśli brak odpowiednich sensorów.
    """
    sensory = _wyciagnij_liste(odpowiedz)
    id_sensora_pm10 = None

    for sensor in sensory:
        kod = (
            sensor.get("Wskaźnik - kod")
            or sensor.get("Wskaźnik - wzór")
            or ""
        ).upper()
        id_sensora = sensor.get("Identyfikator stanowiska")

        if id_sensora is None:
            continue

        if "PM2.5" in kod or "PM25" in kod:
            return (id_sensora, True)
        if "PM10" in kod and id_sensora_pm10 is None:
            id_sensora_pm10 = id_sensora

    return (id_sensora_pm10, False) if id_sensora_pm10 is not None else None


def mapuj_probke(stacja: Station, dane: dict[str, Any], czy_pm25: bool) -> Optional[AirQualitySample]:
    """
    Wyciąga ostatni ważny pomiar z odpowiedzi sensorów.
    Nowe API: lista w kluczu 'Lista danych pomiarowych', pola 'Data' i 'Wartość'.
    """
    pomiary = _wyciagnij_liste(dane)

    for wpis in pomiary:
        wartosc = wpis.get("Wartość")
        if wartosc is None:
            continue

        pm25 = float(wartosc) if czy_pm25 else None
        pm10 = float(wartosc) if not czy_pm25 else None

        timestamp = None
        if wpis.get("Data"):
            try:
                timestamp = datetime.fromisoformat(wpis["Data"])
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
