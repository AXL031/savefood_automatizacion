import { solicitar, solicitarSobre } from "./http";
export type ReglaPromocion = {
  id?: number; version?: number; habilitada: boolean; hora_revision: string; hora_cierre: string;
  stock_umbral: number; descuento_pct: number; descuento_maximo_pct: number;
  antiguedad_maxima_stock_min: number; demora_segundos: number;
};
export type EvaluacionPromocion = {
  id: number; regla: ReglaPromocion; movimiento_id: number; ejecucion_id: number; proponer: boolean;
  descuento_pct: number | null; motivo: string; fecha_hora_simulada: string; creado_en: string;
  lectura: { producto_nombre: string; codigo_lote: string; saldo: number; fecha_limite_venta: string | null; efectivo_en_demo: string };
};
export const leerRegla = (token: string, signal?: AbortSignal) => solicitar<ReglaPromocion | null>("/promociones/regla", { token, signal });
export const guardarRegla = (token: string, regla: ReglaPromocion) => {
  const { id, version, ...body } = regla;
  void id; void version;
  return solicitar<ReglaPromocion>("/promociones/regla", { token, method: "PUT", body });
};
export const listarEvaluacionesPromocion = (token: string, pagina: number, tamano: number, signal?: AbortSignal) => solicitarSobre<EvaluacionPromocion[]>(`/promociones/evaluaciones?limite=${tamano}&desplazamiento=${(pagina - 1) * tamano}`, { token, signal });
