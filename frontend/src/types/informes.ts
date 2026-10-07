import type { EvaluacionTramo } from "./pronostico";

export type TipoInforme = "ventas" | "pronosticos" | "pedidos";
export type FiltrosInforme = { desde?: string; hasta?: string; modelo_id?: number; incluir_evaluacion?: boolean };
export type Informe = {
  generado_en: string;
  periodo: { desde: string; hasta: string; dias_calendario: number; ventas_desde: string | null; ventas_hasta: string | null; pedidos_desde: string | null; pedidos_hasta: string | null };
  fuentes: { ventas: string; pedidos: string; evaluacion: string };
  ventas: {
    unidades: number; registros: number; dias_observados: number; productos_observados: number;
    serie_diaria: { fecha: string; unidades: number; productos_observados: number }[];
    por_producto: { producto_id: number; producto: string; unidades: number; dias_observados: number }[];
  };
  pedidos: { total: number; propuestas: number; propuestas_sin_pedidos: number;
    por_estado: { estado: string; cantidad: number }[]; propuestas_por_estado: { estado: string; cantidad: number }[] };
  evaluacion: EvaluacionTramo | null;
  aviso_evaluacion: string | null;
};

export const etiquetasEstado: Record<string, string> = {
  BLOQUEADO: "Bloqueado", PENDIENTE_APROBACION: "Por aprobar", CANCELADO: "Cancelado", RECHAZADO: "Rechazado",
  PENDIENTE_ENVIO: "Por enviar", ENVIANDO: "Enviando", ENVIADO: "Enviado", FALLIDO: "Fallido",
  PENDIENTE_VERIFICACION: "Verificar envío", GENERADA: "Generada", BLOQUEADA: "Bloqueada",
  SIN_FALTANTES: "Sin faltantes", CANCELADA: "Cancelada",
};
