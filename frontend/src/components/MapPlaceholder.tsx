import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect, useRef } from "react";
import type { RouteCandidate, Station } from "../api/types";

// Leaflet domyślnie nie znajduje ikon w środowiskach bundlerowych — wskazujemy je ręcznie
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

// Kolory tras — rekomendowana zielona, pozostałe szare
const KOLOR_REKOMENDOWANEJ = "#16a34a";
const KOLOR_ZWYKLEJ = "#9ca3af";
const KOLOR_STACJI = "#2563eb";

interface Props {
  kandydaci: RouteCandidate[];
  stacje: Station[];
}

export function MapPlaceholder({ kandydaci, stacje }: Props) {
  const kontenerRef = useRef<HTMLDivElement>(null);
  const mapaRef = useRef<L.Map | null>(null);
  const warstwaTrasRef = useRef<L.LayerGroup | null>(null);
  const warstwaSatcjiRef = useRef<L.LayerGroup | null>(null);

  // Inicjalizacja mapy — tylko raz przy montowaniu komponentu
  useEffect(() => {
    if (!kontenerRef.current || mapaRef.current) return;

    const mapa = L.map(kontenerRef.current).setView([54.4, 18.57], 11);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(mapa);

    warstwaTrasRef.current = L.layerGroup().addTo(mapa);
    warstwaSatcjiRef.current = L.layerGroup().addTo(mapa);
    mapaRef.current = mapa;

    return () => {
      mapa.remove();
      mapaRef.current = null;
    };
  }, []);

  // Rysowanie tras po zmianie kandydatów
  useEffect(() => {
    const warstwa = warstwaTrasRef.current;
    const mapa = mapaRef.current;
    if (!warstwa || !mapa) return;

    warstwa.clearLayers();
    if (kandydaci.length === 0) return;

    const wszystkiePunkty: L.LatLngExpression[] = [];

    kandydaci.forEach((kandydat) => {
      const punkty: L.LatLngExpression[] = kandydat.geometry.map(
        ([lon, lat]) => [lat, lon]
      );

      const linia = L.polyline(punkty, {
        color: kandydat.is_recommended ? KOLOR_REKOMENDOWANEJ : KOLOR_ZWYKLEJ,
        weight: kandydat.is_recommended ? 5 : 3,
        opacity: kandydat.is_recommended ? 0.9 : 0.5,
      });

      const etykieta = kandydat.is_recommended ? "✓ Rekomendowana" : "Trasa alternatywna";
      const pm25 = kandydat.exposure?.avg_pm25?.toFixed(1) ?? "brak";
      const czas = Math.round(kandydat.duration_s / 60);

      linia.bindPopup(`<b>${etykieta}</b><br>Czas: ${czas} min<br>PM2.5 śr: ${pm25} μg/m³`);
      linia.addTo(warstwa);
      wszystkiePunkty.push(...punkty);
    });

    if (wszystkiePunkty.length > 0) {
      mapa.fitBounds(L.latLngBounds(wszystkiePunkty), { padding: [24, 24] });
    }
  }, [kandydaci]);

  // Markery stacji GIOŚ po zmianie listy stacji
  useEffect(() => {
    const warstwa = warstwaSatcjiRef.current;
    if (!warstwa) return;

    warstwa.clearLayers();

    stacje.forEach((stacja) => {
      L.circleMarker([stacja.lat, stacja.lon], {
        radius: 6,
        color: KOLOR_STACJI,
        fillColor: KOLOR_STACJI,
        fillOpacity: 0.7,
        weight: 1,
      })
        .bindPopup(`<b>${stacja.name}</b><br>${stacja.city}`)
        .addTo(warstwa);
    });
  }, [stacje]);

  return (
    <div
      ref={kontenerRef}
      style={{ width: "100%", height: 450, borderRadius: 8, overflow: "hidden" }}
    />
  );
}
