import { useEffect, useState } from "react";
import { pobierzTrybyTransportu } from "../api/client";
import type { GeoPoint, RouteRequest, TransportMode } from "../api/types";

// Presety Trójmiasta do szybkiego testowania
const PRESETY_TROJMIASTO: Record<string, GeoPoint> = {
  "Gdańsk Główny": { lat: 54.3561, lon: 18.6444 },
  "Gdynia Główna": { lat: 54.5189, lon: 18.5319 },
  "Sopot": { lat: 54.4418, lon: 18.5601 },
  "Gdańsk Wrzeszcz": { lat: 54.3794, lon: 18.6094 },
};

interface Props {
  onSubmit: (zapytanie: RouteRequest) => void;
  ladowanie: boolean;
}

export function RoutePlannerForm({ onSubmit, ladowanie }: Props) {
  const [startLat, ustawStartLat] = useState("54.3561");
  const [startLon, ustawStartLon] = useState("18.6444");
  const [endLat, ustawEndLat] = useState("54.5189");
  const [endLon, ustawEndLon] = useState("18.5319");
  const [tryb, ustawTryb] = useState<TransportMode>("walking");
  const [wagaZanieczyszczenia, ustawWageZanieczyszczenia] = useState(0.5);
  const [dostepneTryby, ustawDostepneTryby] = useState<TransportMode[]>([]);

  useEffect(() => {
    pobierzTrybyTransportu()
      .then(ustawDostepneTryby)
      .catch(() => {
        // Fallback gdy backend niedostępny
        ustawDostepneTryby(["walking", "cycling"]);
      });
  }, []);

  function ustawPreset(klucz: string, cel: "start" | "end") {
    const punkt = PRESETY_TROJMIASTO[klucz];
    if (!punkt) return;
    if (cel === "start") {
      ustawStartLat(String(punkt.lat));
      ustawStartLon(String(punkt.lon));
    } else {
      ustawEndLat(String(punkt.lat));
      ustawEndLon(String(punkt.lon));
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      start: { lat: parseFloat(startLat), lon: parseFloat(startLon) },
      end: { lat: parseFloat(endLat), lon: parseFloat(endLon) },
      mode: tryb,
      pollution_weight: wagaZanieczyszczenia,
      alternatives: 3,
    });
  }

  const nazwyTrybow: Record<TransportMode, string> = {
    walking: "Pieszo",
    cycling: "Rowerem",
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <fieldset>
        <legend>Punkt startowy A</legend>
        <select onChange={(e) => ustawPreset(e.target.value, "start")}>
          <option value="">— wybierz preset —</option>
          {Object.keys(PRESETY_TROJMIASTO).map((nazwa) => (
            <option key={nazwa} value={nazwa}>{nazwa}</option>
          ))}
        </select>
        <div style={{ marginTop: 4 }}>
          <label>Szerokość: <input value={startLat} onChange={(e) => ustawStartLat(e.target.value)} style={{ width: 100 }} /></label>
          {" "}
          <label>Długość: <input value={startLon} onChange={(e) => ustawStartLon(e.target.value)} style={{ width: 100 }} /></label>
        </div>
      </fieldset>

      <fieldset>
        <legend>Punkt docelowy B</legend>
        <select onChange={(e) => ustawPreset(e.target.value, "end")}>
          <option value="">— wybierz preset —</option>
          {Object.keys(PRESETY_TROJMIASTO).map((nazwa) => (
            <option key={nazwa} value={nazwa}>{nazwa}</option>
          ))}
        </select>
        <div style={{ marginTop: 4 }}>
          <label>Szerokość: <input value={endLat} onChange={(e) => ustawEndLat(e.target.value)} style={{ width: 100 }} /></label>
          {" "}
          <label>Długość: <input value={endLon} onChange={(e) => ustawEndLon(e.target.value)} style={{ width: 100 }} /></label>
        </div>
      </fieldset>

      <div>
        <label>Środek transportu: </label>
        <select value={tryb} onChange={(e) => ustawTryb(e.target.value as TransportMode)}>
          {dostepneTryby.map((t) => (
            <option key={t} value={t}>{nazwyTrybow[t] ?? t}</option>
          ))}
        </select>
      </div>

      <div>
        <label>
          Priorytet: szybkość ←→ czystość powietrza
          <br />
          <input
            type="range"
            min={0}
            max={1}
            step={0.1}
            value={wagaZanieczyszczenia}
            onChange={(e) => ustawWageZanieczyszczenia(parseFloat(e.target.value))}
            style={{ width: 200 }}
          />
          {" "}{Math.round(wagaZanieczyszczenia * 100)}% czystość
        </label>
      </div>

      <button type="submit" disabled={ladowanie}>
        {ladowanie ? "Szukam…" : "Szukaj trasy"}
      </button>
    </form>
  );
}
