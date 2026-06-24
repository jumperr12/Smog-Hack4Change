import { useEffect, useState } from "react";
import { pobierzTrybyTransportu } from "../api/client";
import type { GeoPoint, RouteRequest, TransportMode } from "../api/types";
import { AddressSearch } from "./AddressSearch";

interface Props {
  onSubmit: (zapytanie: RouteRequest) => void;
  ladowanie: boolean;
}

export function RoutePlannerForm({ onSubmit, ladowanie }: Props) {
  const [punktStart, ustawPunktStart] = useState<GeoPoint | null>({ lat: 54.3561, lon: 18.6444 });
  const [punktKoniec, ustawPunktKoniec] = useState<GeoPoint | null>({ lat: 54.5189, lon: 18.5319 });
  const [tryb, ustawTryb] = useState<TransportMode>("walking");
  const [wagaZanieczyszczenia, ustawWageZanieczyszczenia] = useState(0.5);
  const [dostepneTryby, ustawDostepneTryby] = useState<TransportMode[]>([]);

  useEffect(() => {
    pobierzTrybyTransportu()
      .then(ustawDostepneTryby)
      .catch(() => ustawDostepneTryby(["walking", "cycling"]));
  }, []);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!punktStart || !punktKoniec) return;
    onSubmit({
      start: punktStart,
      end: punktKoniec,
      mode: tryb,
      pollution_weight: wagaZanieczyszczenia,
      alternatives: 3,
    });
  }

  const nazwyTrybow: Record<TransportMode, string> = {
    walking: "Pieszo",
    cycling: "Rowerem",
  };

  const moznaWyslac = punktStart !== null && punktKoniec !== null && !ladowanie;

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <AddressSearch
        label="Punkt startowy A"
        wartoscPoczatkowa="Gdańsk Główny"
        onWybierz={(punkt) => ustawPunktStart(punkt)}
      />

      <AddressSearch
        label="Punkt docelowy B"
        wartoscPoczatkowa="Gdynia Główna"
        onWybierz={(punkt) => ustawPunktKoniec(punkt)}
      />

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

      <button type="submit" disabled={!moznaWyslac}>
        {ladowanie ? "Szukam…" : "Szukaj trasy"}
      </button>

      {(!punktStart || !punktKoniec) && (
        <p style={{ color: "#888", fontSize: 13, margin: 0 }}>
          Wybierz punkt startowy i docelowy z listy podpowiedzi.
        </p>
      )}
    </form>
  );
}
