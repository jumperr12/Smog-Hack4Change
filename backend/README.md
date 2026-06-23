# Backend — Smog Route Optimizer

FastAPI + Python 3.11+

## Uruchomienie

```bash
cp .env.example .env   # uzupełnij ORS_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/docs

## Testy

```bash
pytest tests/ -v
```

## Wymagane zmienne środowiskowe

| Zmienna | Opis | Domyślna |
|---------|------|---------|
| `ORS_API_KEY` | Klucz OpenRouteService (rejestracja: openrouteservice.org) | — |
| `GIOS_BASE_URL` | Base URL API GIOŚ | `https://api.gios.gov.pl/pjp-api/rest` |
| `AIR_QUALITY_PROVIDER` | Aktywny provider smogu | `gios` |
| `ROUTING_PROVIDER` | Aktywny provider tras | `openrouteservice` |
| `BBOX_*` | Obszar geograficzny | Trójmiasto |
