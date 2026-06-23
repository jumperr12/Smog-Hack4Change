import type {
  AirQualitySample,
  RouteRequest,
  RouteResponse,
  Station,
  TransportMode,
} from "./types";

const BASE_URL = "/api";

async function pobierzJson<T>(url: string, opcje?: RequestInit): Promise<T> {
  const odpowiedz = await fetch(url, opcje);
  if (!odpowiedz.ok) {
    throw new Error(`Błąd HTTP ${odpowiedz.status}: ${await odpowiedz.text()}`);
  }
  return odpowiedz.json() as Promise<T>;
}

export async function pobierzStacje(bbox?: {
  minLat: number;
  minLon: number;
  maxLat: number;
  maxLon: number;
}): Promise<Station[]> {
  const parametry = new URLSearchParams();
  if (bbox) {
    parametry.set("min_lat", String(bbox.minLat));
    parametry.set("min_lon", String(bbox.minLon));
    parametry.set("max_lat", String(bbox.maxLat));
    parametry.set("max_lon", String(bbox.maxLon));
  }
  const zapytanie = parametry.size > 0 ? `?${parametry}` : "";
  return pobierzJson<Station[]>(`${BASE_URL}/air-quality/stations${zapytanie}`);
}

export async function pobierzJakoscPowietrza(
  lat: number,
  lon: number
): Promise<AirQualitySample | null> {
  return pobierzJson<AirQualitySample | null>(
    `${BASE_URL}/air-quality?lat=${lat}&lon=${lon}`
  );
}

export async function pobierzTrybyTransportu(): Promise<TransportMode[]> {
  return pobierzJson<TransportMode[]>(`${BASE_URL}/transport-modes`);
}

export async function wyznaczTrase(
  zapytanie: RouteRequest
): Promise<RouteResponse> {
  return pobierzJson<RouteResponse>(`${BASE_URL}/routes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(zapytanie),
  });
}
