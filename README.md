# Smog Route Optimizer — Hack4Change

Aplikacja wyznacza trasę z punktu A do B minimalizując ekspozycję na zanieczyszczenie powietrza (smog), przy zachowaniu rozsądnego czasu przejazdu. Obsługuje transport pieszy i rowerowy.

## Szybki start

```bash
# Backend
cd backend
cp .env.example .env       # uzupełnij ORS_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload
# API dostępne na http://localhost:8000/docs

# Frontend (osobny terminal)
cd frontend
npm install
npm run dev
# UI dostępne na http://localhost:5173
```

## Architektura

```
backend/app/
├── models/          — kontrakt danych (Pydantic → OpenAPI → typy TS)
│   ├── geo.py       — GeoPoint, BBox
│   ├── air_quality.py — Station, AirQualitySample
│   └── routing.py   — RouteRequest, RouteCandidate, ExposureProfile, RouteResponse
├── core/            — czysta logika bez zależności sieciowych
│   ├── geo_utils.py   — haversine, resample geometrii
│   ├── interpolation.py — IDW i nearest-neighbor dla rzadkiej sieci stacji
│   ├── sampler.py   — próbkowanie smogu wzdłuż trasy
│   ├── cost.py      — funkcja kosztu (strategia, łatwa do podmiany)
│   └── optimizer.py — orkiestracja: trasy → smog → ranking
├── providers/       — adaptery do zewnętrznych API
│   ├── air_quality/
│   │   ├── base.py  — AirQualityProvider (ABC)
│   │   └── gios/    — implementacja GIOŚ (bez klucza)
│   └── routing/
│       ├── base.py  — RoutingProvider (ABC)
│       └── openrouteservice/ — implementacja ORS (klucz API)
└── api/             — endpointy FastAPI

frontend/src/
├── api/             — typy TS + typowany klient fetch
├── hooks/           — useRouteOptimizer (stan zapytania)
└── components/      — formularz, wyniki, placeholder mapy
```

## Endpointy

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/health` | liveness |
| GET | `/api/transport-modes` | dostępne środki transportu |
| GET | `/api/air-quality/stations` | stacje GIOŚ w obszarze (bbox) |
| GET | `/api/air-quality?lat=&lon=` | jakość powietrza w punkcie |
| POST | `/api/routes` | główny endpoint optymalizacji |
| WS | `/ws/routes` | stub — do rozbudowy |

### Przykład zapytania POST /api/routes

```json
{
  "start": { "lat": 54.3561, "lon": 18.6444 },
  "end":   { "lat": 54.5189, "lon": 18.5319 },
  "mode": "cycling",
  "pollution_weight": 0.7,
  "alternatives": 3
}
```

`pollution_weight`: `0.0` = najszybsza trasa, `1.0` = najczystsza powietrznie.

## Jak dodać nowe miasto

W `.env` zmień bbox:
```env
BBOX_MIN_LAT=50.00
BBOX_MIN_LON=19.80
BBOX_MAX_LAT=50.12
BBOX_MAX_LON=20.10
```

## Jak dodać nowe źródło danych (np. Airly)

1. Stwórz `backend/app/providers/air_quality/airly/` z `client.py`, `mapping.py`, `provider.py`
2. Podklasa `AirQualityProvider` z implementacją `get_stations`, `get_air_quality_at`, `get_samples_near`
3. Zarejestruj w `providers/registry.py`
4. Ustaw `AIR_QUALITY_PROVIDER=airly` w `.env`

## Jak dodać nowy środek transportu

1. Dodaj wartość do `TransportMode` w `backend/app/models/routing.py`
2. Dodaj mapowanie profilu w `providers/routing/openrouteservice/provider.py`
3. Zaktualizuj `frontend/src/api/types.ts`

## Testy

```bash
cd backend
pytest tests/ -v
```

19 testów, zero sieci — providery mockowane przez zaślepki.
