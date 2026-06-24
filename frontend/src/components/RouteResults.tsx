import type { RouteCandidate } from "../api/types";

interface Props {
  kandydaci: RouteCandidate[];
  wybranyIndeks: number | null;
  onWybierz: (indeks: number) => void;
}

function formatujCzas(sekundy: number): string {
  const minuty = Math.round(sekundy / 60);
  if (minuty < 60) return `${minuty} min`;
  const godziny = Math.floor(minuty / 60);
  const pozostaleMinuty = minuty % 60;
  return `${godziny}h ${pozostaleMinuty}min`;
}

function formatujDystans(metry: number): string {
  if (metry < 1000) return `${Math.round(metry)} m`;
  return `${(metry / 1000).toFixed(1)} km`;
}

function formatujPm25(wartosc: number | null): string {
  if (wartosc === null) return "brak danych";
  return `${wartosc.toFixed(1)} μg/m³`;
}

export function RouteResults({ kandydaci, wybranyIndeks, onWybierz }: Props) {
  if (kandydaci.length === 0) {
    return <p>Brak wyników.</p>;
  }

  return (
    <div>
      <h3>Znalezione trasy ({kandydaci.length}) — kliknij żeby wybrać</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {kandydaci.map((kandydat, indeks) => {
          const wybrana = indeks === wybranyIndeks;
          return (
            <div
              key={indeks}
              onClick={() => onWybierz(indeks)}
              style={{
                border: wybrana
                  ? "2px solid #1d4ed8"
                  : kandydat.is_recommended
                  ? "2px solid #16a34a"
                  : "1px solid #ccc",
                background: wybrana ? "#eff6ff" : "white",
                padding: 12,
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              <strong>
                {wybrana ? "▶ " : ""}
                Trasa {indeks + 1}
                {kandydat.is_recommended && " ✓ Rekomendowana"}
              </strong>
              <table style={{ marginTop: 6, borderCollapse: "collapse" }}>
                <tbody>
                  <tr>
                    <td style={{ paddingRight: 16 }}>Czas</td>
                    <td>{formatujCzas(kandydat.duration_s)}</td>
                  </tr>
                  <tr>
                    <td>Dystans</td>
                    <td>{formatujDystans(kandydat.distance_m)}</td>
                  </tr>
                  <tr>
                    <td>Średnie PM2.5</td>
                    <td>{formatujPm25(kandydat.exposure?.avg_pm25 ?? null)}</td>
                  </tr>
                  <tr>
                    <td>Szczytowe PM2.5</td>
                    <td>{formatujPm25(kandydat.exposure?.peak_pm25 ?? null)}</td>
                  </tr>
                  {kandydat.cost !== null && (
                    <tr>
                      <td>Koszt (niżej = lepiej)</td>
                      <td>{kandydat.cost.toFixed(3)}</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          );
        })}
      </div>
    </div>
  );
}
