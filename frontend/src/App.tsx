import { useCallback, useEffect, useState } from "react";
import { pobierzStacje } from "./api/client";
import type { RouteRequest, Station } from "./api/types";
import { MapPlaceholder } from "./components/MapPlaceholder";
import { RoutePlannerForm } from "./components/RoutePlannerForm";
import { RouteResults } from "./components/RouteResults";
import { useRouteOptimizer } from "./hooks/useRouteOptimizer";

export function App() {
  const { wynik, ladowanie, blad, szukajTrasy } = useRouteOptimizer();
  const [stacje, ustawStacje] = useState<Station[]>([]);
  const [wybranyIndeks, ustawWybranyIndeks] = useState<number | null>(null);

  useEffect(() => {
    pobierzStacje()
      .then(ustawStacje)
      .catch(() => {});
  }, []);

  // Po nowym wyszukiwaniu ustaw rekomendowaną jako domyślnie wybraną
  useEffect(() => {
    if (wynik) {
      ustawWybranyIndeks(wynik.recommended_index ?? 0);
    }
  }, [wynik]);

  const handleSzukaj = useCallback(
    (zapytanie: RouteRequest) => {
      ustawWybranyIndeks(null);
      szukajTrasy(zapytanie);
    },
    [szukajTrasy]
  );

  const handleWybierzTrase = useCallback((indeks: number) => {
    ustawWybranyIndeks(indeks);
  }, []);

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24, fontFamily: "sans-serif" }}>
      <h1 style={{ marginBottom: 4 }}>Smog Route Optimizer</h1>
      <p style={{ color: "#666", marginTop: 0 }}>
        Wyznacza trasę z punktu A do B uwzględniając zanieczyszczenie powietrza — Trójmiasto
      </p>

      <RoutePlannerForm onSubmit={handleSzukaj} ladowanie={ladowanie} />

      <div style={{ marginTop: 24 }}>
        <MapPlaceholder
          kandydaci={wynik?.candidates ?? []}
          stacje={stacje}
          wybranyIndeks={wybranyIndeks}
          onWybierzTrase={handleWybierzTrase}
        />
      </div>

      {blad && (
        <div style={{ marginTop: 16, color: "red" }}>
          Błąd: {blad}
        </div>
      )}

      {wynik && (
        <div style={{ marginTop: 24 }}>
          <RouteResults
            kandydaci={wynik.candidates}
            wybranyIndeks={wybranyIndeks}
            onWybierz={handleWybierzTrase}
          />
        </div>
      )}
    </div>
  );
}
