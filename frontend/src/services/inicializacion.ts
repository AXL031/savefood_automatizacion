import { solicitar } from "./http";
import type { ResultadoCargaPiloto } from "@/types/inicializacion";

export function cargarCsvPiloto(token: string, archivo: File): Promise<ResultadoCargaPiloto> {
  const formData = new FormData();
  formData.append("archivo", archivo);
  return solicitar<ResultadoCargaPiloto>("/inicializacion/piloto-bakery", {
    token, method: "POST", formData,
  });
}
