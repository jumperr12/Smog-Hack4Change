import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect, useRef } from "react";
import type { RouteCandidate, Station } from "../api/types";

delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const KOLOR_WYBRANEJ = "#1d4ed8";
const KOLOR_REKOMENDOWANEJ = "#16a34a";
const KOLOR_ZWYKLEJ = "#9ca3af";
const KOLOR_STACJI = "#2563eb";

interface Props {
  kandydaci: RouteCandidate[];
  stacje: Station[];
  wybranyIndeks: number | null;
  onWybierzTrase: (indeks: number) => void;
}

export function MapPlaceholder({ kandydaci, stacje, wybranyIndeks, onWybierzTrase }: Props) {
  const kontenerRef = useRef<HTMLDivElement>(null);
  const mapaRef = useRef<L.Map | null>(null);
  const warstwaTrasRef = useRef<L.LayerGroup | null>(null);
  const warstwaSatcjiRef = useRef<L.LayerGroup | null>(null);

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

  // Przerysowanie tras przy zmianie kandydatów lub wybranego indeksu
  useEffect(() => {
    const warstwa = warstwaTrasRef.current;
    const mapa = mapaRef.current;
    if (!warstwa || !mapa) return;

    warstwa.clearLayers();
    if (kandydaci.length === 0) return;

    const wszystkiePunkty: L.LatLngExpression[] = [];

    // Rysuj najpierw nieaktywne, żeby wybrana była zawsze na wierzchu
    const posortowaneIndeksy = kandydaci
      .map((_, i) => i)
      .sort((a, b) => {
        if (a === wybranyIndeks) return 1;
        if (b === wybranyIndeks) return -1;
        return 0;
      });

    posortowaneIndeksy.forEach((indeks) => {
      const kandydat = kandydaci[indeks];
      const wybrana = indeks === wybranyIndeks;

      const punkty: L.LatLngExpression[] = kandydat.geometry.map(
        ([lon, lat]) => [lat, lon]
      );

      let kolor = KOLOR_ZWYKLEJ;
      if (wybrana) kolor = KOLOR_WYBRANEJ;
      else if (kandydat.is_recommended) kolor = KOLOR_REKOMENDOWANEJ;

      const linia = L.polyline(punkty, {
        color: kolor,
        weight: wybrana ? 7 : kandydat.is_recommended ? 5 : 3,
        opacity: wybrana ? 1 : kandydat.is_recommended ? 0.85 : 0.45,
      });

      const etykieta = wybrana
        ? `▶ Trasa ${indeks + 1} (wybrana)`
        : kandydat.is_recommended
        ? `✓ Trasa ${indeks + 1} (rekomendowana)`
        : `Trasa ${indeks + 1}`;
      const pm25 = kandydat.exposure?.avg_pm25?.toFixed(1) ?? "brak";
      const czas = Math.round(kandydat.duration_s / 60);

      linia.bindPopup(`<b>${etykieta}</b><br>Czas: ${czas} min<br>PM2.5 śr: ${pm25} μg/m³`);
      linia.on("click", () => onWybierzTrase(indeks));
      linia.addTo(warstwa);
      wszystkiePunkty.push(...punkty);
    });

    if (wszystkiePunkty.length > 0) {
      mapa.fitBounds(L.latLngBounds(wszystkiePunkty), { padding: [24, 24] });
    }
  }, [kandydaci, wybranyIndeks, onWybierzTrase]);

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
