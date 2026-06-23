import { useState } from "react";
import { wyznaczTrase } from "../api/client";
import type { RouteRequest, RouteResponse } from "../api/types";

interface StanOptymalizatora {
  wynik: RouteResponse | null;
  ladowanie: boolean;
  blad: string | null;
}

interface UseRouteOptimizer extends StanOptymalizatora {
  szukajTrasy: (zapytanie: RouteRequest) => Promise<void>;
  resetuj: () => void;
}

export function useRouteOptimizer(): UseRouteOptimizer {
  const [wynik, ustawWynik] = useState<RouteResponse | null>(null);
  const [ladowanie, ustawLadowanie] = useState(false);
  const [blad, ustawBlad] = useState<string | null>(null);

  async function szukajTrasy(zapytanie: RouteRequest): Promise<void> {
    ustawLadowanie(true);
    ustawBlad(null);
    ustawWynik(null);

    try {
      const odpowiedz = await wyznaczTrase(zapytanie);
      ustawWynik(odpowiedz);
    } catch (error) {
      ustawBlad(error instanceof Error ? error.message : "Nieznany błąd");
    } finally {
      ustawLadowanie(false);
    }
  }

  function resetuj(): void {
    ustawWynik(null);
    ustawBlad(null);
  }

  return { wynik, ladowanie, blad, szukajTrasy, resetuj };
}
