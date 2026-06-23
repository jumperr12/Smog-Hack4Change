// Typy TS odzwierciedlają modele Pydantic z backendu 1:1
// Przy zmianie modelu w backend/app/models/ — zaktualizować tutaj

export interface GeoPoint {
  lat: number;
  lon: number;
}

export interface Station {
  id: number;
  name: string;
  lat: number;
  lon: number;
  city: string;
}

export interface AirQualitySample {
  lat: number;
  lon: number;
  pm25: number | null;
  pm10: number | null;
  aqi_index: string | null;
  source: string;
  timestamp: string | null;
}

export type TransportMode = "walking" | "cycling";

export interface RouteRequest {
  start: GeoPoint;
  end: GeoPoint;
  mode: TransportMode;
  pollution_weight: number; // 0.0–1.0
  alternatives: number;
}

export interface ExposureSamplePoint {
  lat: number;
  lon: number;
  pm25: number | null;
}

export interface ExposureProfile {
  total_exposure: number;
  avg_pm25: number | null;
  peak_pm25: number | null;
  sample_count: number;
  samples: ExposureSamplePoint[];
}

export interface RouteCandidate {
  geometry: [number, number][]; // [[lon, lat], ...] format GeoJSON
  distance_m: number;
  duration_s: number;
  mode: TransportMode;
  exposure: ExposureProfile | null;
  cost: number | null;
  is_recommended: boolean;
}

export interface RouteResponse {
  request: RouteRequest;
  candidates: RouteCandidate[];
  recommended_index: number | null;
}
