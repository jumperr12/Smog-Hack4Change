import pytest

from app.core.geo_utils import haversine, punkt_w_bbox, resample_geometrie
from app.models.geo import BBox, GeoPoint


def test_haversine_ten_sam_punkt():
    punkt = GeoPoint(lat=54.35, lon=18.65)
    assert haversine(punkt, punkt) == 0.0


def test_haversine_gdansk_gdynia():
    # Gdańsk Główny → Gdynia Główna, linia prosta ok. 20–22 km
    gdansk = GeoPoint(lat=54.3520, lon=18.6466)
    gdynia = GeoPoint(lat=54.5189, lon=18.5319)
    odleglosc = haversine(gdansk, gdynia)
    assert 19_000 < odleglosc < 23_000


def test_haversine_symetria():
    punkt_a = GeoPoint(lat=54.35, lon=18.65)
    punkt_b = GeoPoint(lat=54.52, lon=18.53)
    assert haversine(punkt_a, punkt_b) == pytest.approx(haversine(punkt_b, punkt_a))


def test_resample_zwraca_wiecej_punktow_niz_wejscie():
    geometria = [[18.644, 54.356], [18.531, 54.519]]
    punkty = resample_geometrie(geometria, 200.0)
    assert len(punkty) > 2


def test_resample_pusty_wejscie():
    assert resample_geometrie([], 200.0) == []


def test_resample_jeden_punkt():
    geometria = [[18.65, 54.35]]
    punkty = resample_geometrie(geometria, 200.0)
    assert len(punkty) == 1


def test_punkt_w_bbox_wewnatrz():
    bbox = BBox(min_lat=54.25, min_lon=18.40, max_lat=54.60, max_lon=18.80)
    punkt = GeoPoint(lat=54.35, lon=18.65)
    assert punkt_w_bbox(punkt, bbox) is True


def test_punkt_w_bbox_na_zewnatrz():
    bbox = BBox(min_lat=54.25, min_lon=18.40, max_lat=54.60, max_lon=18.80)
    punkt = GeoPoint(lat=50.00, lon=20.00)
    assert punkt_w_bbox(punkt, bbox) is False


def test_punkt_w_bbox_na_granicy():
    bbox = BBox(min_lat=54.25, min_lon=18.40, max_lat=54.60, max_lon=18.80)
    punkt = GeoPoint(lat=54.25, lon=18.40)
    assert punkt_w_bbox(punkt, bbox) is True
