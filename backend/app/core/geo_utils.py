import math
from typing import List

from ..models.geo import BBox, GeoPoint

PROMIEN_ZIEMI_M = 6_371_000


def haversine(punkt_a: GeoPoint, punkt_b: GeoPoint) -> float:
    """Odległość między dwoma punktami geograficznymi w metrach (formuła haversine)."""
    lat1 = math.radians(punkt_a.lat)
    lon1 = math.radians(punkt_a.lon)
    lat2 = math.radians(punkt_b.lat)
    lon2 = math.radians(punkt_b.lon)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return PROMIEN_ZIEMI_M * c


def resample_geometrie(wspolrzedne: List[List[float]], co_ile_metrow: float) -> List[GeoPoint]:
    """
    Rozmieszcza równomiernie punkty wzdłuż geometrii trasy co podaną liczbę metrów.
    wspolrzedne to lista [lon, lat] w formacie GeoJSON.
    """
    if not wspolrzedne:
        return []
    if len(wspolrzedne) == 1:
        return [GeoPoint(lat=wspolrzedne[0][1], lon=wspolrzedne[0][0])]

    punkty_wynikowe: List[GeoPoint] = []
    # Odległość do następnego punktu próbkowania — przenosi się między segmentami
    pozostalo_do_proby = 0.0

    for i in range(len(wspolrzedne) - 1):
        punkt_start = GeoPoint(lat=wspolrzedne[i][1], lon=wspolrzedne[i][0])
        punkt_koniec = GeoPoint(lat=wspolrzedne[i + 1][1], lon=wspolrzedne[i + 1][0])

        dlugosc_segmentu = haversine(punkt_start, punkt_koniec)
        if dlugosc_segmentu == 0:
            continue

        przebyta = pozostalo_do_proby
        while przebyta <= dlugosc_segmentu:
            udzial = przebyta / dlugosc_segmentu
            lat = punkt_start.lat + udzial * (punkt_koniec.lat - punkt_start.lat)
            lon = punkt_start.lon + udzial * (punkt_koniec.lon - punkt_start.lon)
            punkty_wynikowe.append(GeoPoint(lat=lat, lon=lon))
            przebyta += co_ile_metrow

        pozostalo_do_proby = przebyta - dlugosc_segmentu

    # Zawsze dodaj ostatni punkt trasy
    ostatni = wspolrzedne[-1]
    punkty_wynikowe.append(GeoPoint(lat=ostatni[1], lon=ostatni[0]))

    return punkty_wynikowe


def punkt_w_bbox(punkt: GeoPoint, bbox: BBox) -> bool:
    """Sprawdza czy punkt leży wewnątrz prostokąta ograniczającego."""
    return (
        bbox.min_lat <= punkt.lat <= bbox.max_lat
        and bbox.min_lon <= punkt.lon <= bbox.max_lon
    )
