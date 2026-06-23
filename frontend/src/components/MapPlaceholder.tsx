import type { RouteCandidate, Station } from "../api/types";

interface Props {
  // Kontrakt komponentu mapy — zastąp MapPlaceholder biblioteką (Leaflet, MapLibre, deck.gl)
  // i przekaż te same propsy do rzeczywistej mapy
  kandydaci: RouteCandidate[];
  stacje: Station[];
}

export function MapPlaceholder({ kandydaci, stacje }: Props) {
  const liczbaKandydatow = kandydaci.length;
  const liczbaStacji = stacje.length;

  return (
    <div
      style={{
        width: "100%",
        height: 400,
        background: "#f0f0f0",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        border: "2px dashed #aaa",
        borderRadius: 8,
        color: "#666",
        fontSize: 14,
      }}
    >
      <p style={{ fontWeight: "bold", margin: 0 }}>[ Placeholder mapy ]</p>
      <p style={{ margin: "8px 0 0" }}>
        Podłącz tutaj Leaflet lub MapLibre GL — ten komponent otrzymuje:
      </p>
      <ul style={{ textAlign: "left", marginTop: 4 }}>
        <li>
          <code>kandydaci</code> — {liczbaKandydatow} tras do narysowania (geometria GeoJSON,
          rekomendowana wyróżniona kolorem)
        </li>
        <li>
          <code>stacje</code> — {liczbaStacji} stacji GIOŚ (markery z wartością PM2.5)
        </li>
      </ul>
    </div>
  );
}
