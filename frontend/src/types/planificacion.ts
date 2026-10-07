export type ResumenPlan = {
  id: number; corrida_id: number; ejecucion_id: number; fecha_objetivo: string;
  clave_ejecucion: string; huella_stock_recetas: string; stock_leido_en: string;
  creado_en: string; estado: "PROPUESTO"; margen_seguridad: number;
};
export type ElementoPlan = {
  id: number; producto_id: number; producto: string; pronostico_id: number;
  receta_id: number; receta_version: number; cantidad_pronosticada: number;
  stock_disponible: number; cantidad_producir: number; vigencia_stock_desconocida: boolean;
};
export type Necesidad = {
  id: number; ingrediente_id: number; ingrediente: string; unidad: string;
  cantidad_requerida: string; cantidad_disponible: string | null; cantidad_faltante: string | null;
  stock_conocido: boolean; vigencia_stock_desconocida: boolean;
};
export type Plan = ResumenPlan & {
  elementos: ElementoPlan[]; necesidades: Necesidad[];
  omisiones: { producto_id: number; producto: string; motivo: string }[]; avisos: string[];
  trazas: {
    modelo_id: number;
    recetas: Record<string, { receta_id: number; version: number; lineas: {
      ingrediente_id: number; nombre: string; cantidad_por_unidad: string; unidad_base: string;
    }[] }>;
    stock: { fecha: string; huella: string; items: {
      tipo: string; item_id: number; nombre: string; unidad: string;
      lotes: { lote_id: number; codigo_lote: string; saldo: string; cuenta: boolean; motivo: string }[];
    }[] };
  };
};
