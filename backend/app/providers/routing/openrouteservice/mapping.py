from typing import Any, List

from ....models.routing import RouteCandidate, TransportMode


def mapuj_kandydatow(odpowiedz: dict[str, Any], tryb: TransportMode) -> List[RouteCandidate]:
    """
    Mapuje odpowiedź GeoJSON FeatureCollection z ORS na listę RouteCandidate.
    Każdy Feature to osobna trasa (główna lub alternatywna).
    """
    kandydaci = []

    for feature in odpowiedz.get("features", []):
        geometria: List[List[float]] = feature.get("geometry", {}).get("coordinates", [])
        podsumowanie: dict[str, Any] = feature.get("properties", {}).get("summary", {})

        if not geometria or not podsumowanie:
            continue

        kandydaci.append(
            RouteCandidate(
                geometry=geometria,
                distance_m=podsumowanie.get("distance", 0.0),
                duration_s=podsumowanie.get("duration", 0.0),
                mode=tryb,
            )
        )

    return kandydaci
