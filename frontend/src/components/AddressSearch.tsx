import { useEffect, useRef, useState } from "react";
import type { GeoPoint } from "../api/types";

interface WynikNominatim {
  place_id: number;
  display_name: string;
  lat: string;
  lon: string;
}

interface Props {
  label: string;
  wartoscPoczatkowa?: string;
  onWybierz: (punkt: GeoPoint, etykieta: string) => void;
}

export function AddressSearch({ label, wartoscPoczatkowa = "", onWybierz }: Props) {
  const [zapytanie, ustawZapytanie] = useState(wartoscPoczatkowa);
  const [wyniki, ustawWyniki] = useState<WynikNominatim[]>([]);
  const [pokazDropdown, ustawPokazDropdown] = useState(false);
  const [szukanie, ustawSzukanie] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const kontenerRef = useRef<HTMLDivElement>(null);

  // Zamknij dropdown przy kliknięciu poza komponentem
  useEffect(() => {
    function klikniecieNaZewnatz(zdarzenie: MouseEvent) {
      if (kontenerRef.current && !kontenerRef.current.contains(zdarzenie.target as Node)) {
        ustawPokazDropdown(false);
      }
    }
    document.addEventListener("mousedown", klikniecieNaZewnatz);
    return () => document.removeEventListener("mousedown", klikniecieNaZewnatz);
  }, []);

  function handleZmiana(nowaWartosc: string) {
    ustawZapytanie(nowaWartosc);
    ustawPokazDropdown(false);

    if (timerRef.current) clearTimeout(timerRef.current);

    if (nowaWartosc.trim().length < 3) {
      ustawWyniki([]);
      return;
    }

    timerRef.current = setTimeout(async () => {
      ustawSzukanie(true);
      try {
        const parametry = new URLSearchParams({
          q: nowaWartosc,
          format: "json",
          limit: "6",
          countrycodes: "pl",
          addressdetails: "0",
        });
        const odpowiedz = await fetch(
          `https://nominatim.openstreetmap.org/search?${parametry}`,
          { headers: { "Accept-Language": "pl", "User-Agent": "SmogRouteOptimizer/1.0" } }
        );
        const dane: WynikNominatim[] = await odpowiedz.json();
        ustawWyniki(dane);
        ustawPokazDropdown(dane.length > 0);
      } catch {
        ustawWyniki([]);
      } finally {
        ustawSzukanie(false);
      }
    }, 350);
  }

  function handleWybierz(wynik: WynikNominatim) {
    ustawZapytanie(wynik.display_name);
    ustawPokazDropdown(false);
    ustawWyniki([]);
    onWybierz(
      { lat: parseFloat(wynik.lat), lon: parseFloat(wynik.lon) },
      wynik.display_name
    );
  }

  return (
    <div ref={kontenerRef} style={{ position: "relative" }}>
      <label style={{ display: "block", marginBottom: 4 }}>{label}</label>
      <div style={{ position: "relative" }}>
        <input
          type="text"
          value={zapytanie}
          onChange={(e) => handleZmiana(e.target.value)}
          onFocus={() => wyniki.length > 0 && ustawPokazDropdown(true)}
          placeholder="Wpisz adres lub nazwę miejsca…"
          style={{ width: "100%", padding: "6px 8px", boxSizing: "border-box" }}
        />
        {szukanie && (
          <span style={{ position: "absolute", right: 8, top: "50%", transform: "translateY(-50%)", color: "#999", fontSize: 12 }}>
            szukam…
          </span>
        )}
      </div>

      {pokazDropdown && wyniki.length > 0 && (
        <ul
          style={{
            position: "absolute",
            zIndex: 1000,
            background: "white",
            border: "1px solid #ccc",
            borderTop: "none",
            margin: 0,
            padding: 0,
            listStyle: "none",
            width: "100%",
            maxHeight: 240,
            overflowY: "auto",
            boxShadow: "0 4px 8px rgba(0,0,0,0.15)",
          }}
        >
          {wyniki.map((wynik) => (
            <li
              key={wynik.place_id}
              onMouseDown={() => handleWybierz(wynik)}
              style={{
                padding: "8px 10px",
                cursor: "pointer",
                fontSize: 13,
                borderBottom: "1px solid #f0f0f0",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#f0f7ff")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "white")}
            >
              {wynik.display_name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
