import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";

const kontener = document.getElementById("root");
if (!kontener) throw new Error("Brak elementu #root w DOM");

createRoot(kontener).render(
  <StrictMode>
    <App />
  </StrictMode>
);
