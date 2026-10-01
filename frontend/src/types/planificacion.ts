import type { DisponibilidadItem } from "./inventario";

export type EstadoElementoPlan = "CALCULADO" | "HISTORIAL_INSUFICIENTE" | "PRODUCTO_NO_CUBIERTO" | "SIN_RECETA" | "STOCK_DESCONOCIDO";
export type RecetaPlan = {
  receta_id: number; version: number;
  lineas: { ingrediente_id: number; codigo: string; nombre: string; unidad_base: string; cantidad_por_unidad: string }[];
};
export type ElementoPlan = {
  producto_id: number; pronostico_id: number;
  cantidad_pronosticada: number | null; stock_disponible: number | null; cantidad_producir: number | null;
  estado: EstadoElementoPlan; avisos: string[]; receta: RecetaPlan | null; stock: DisponibilidadItem;
};
export type ResumenPlan = {
  id: number; corrida_id: number; ejecucion_id: number; clave_ejecucion: string;
  fecha_objetivo: string; estado: "PROPUESTO"; version_calculo: string;
  stock_leido_en: string; creado_en: string; huella_stock_recetas: string;
  origen_pronostico: { modelo_id: number; version_modelo: string; huella_datos_entrada: string };
  necesidades_estado: "PENDIENTE_M03" | "CALCULADAS" | "INCOMPLETAS"; pedidos_estado: "PENDIENTE_GENERACION" | "GENERADA" | "BLOQUEADA" | "SIN_FALTANTES" | "CANCELADA";
};
export type Plan = ResumenPlan & {
  elementos: ElementoPlan[];
  necesidades_meta: { version: string; stock_leido_en: string; vigencia_desconocida: boolean; productos_excluidos: { producto_id: number; nombre: string; estado: string }[] } | null;
  necesidades: { ingrediente_id: number; unidad_base: string; cantidad_necesaria: string; stock_disponible: string | null; faltante: string | null; estado: string; stock: DisponibilidadItem; aportes: { producto_id: number; receta_id: number; version_receta: number; cantidad_producir: number; cantidad_por_unidad: string; aporte: string }[] }[];
};
