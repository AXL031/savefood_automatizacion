export type Particion = {
  inicio_entrenamiento: string; fin_entrenamiento: string;
  inicio_validacion: string; fin_validacion: string;
  inicio_prueba: string; fin_prueba: string;
};

export type Metricas = {
  total_pronosticados: number; pares_evaluables: number; productos_excluidos: number;
  cobertura_pct: number; mae: number | null; wape_pct: number | null;
  dentro_mas_menos_20_pct: number | null; dentro_mas_menos_10_pct: number | null;
};

export type Modelo = {
  id: number; version_modelo: string; estado: string; sha256: string;
  fecha_corte_entrenamiento: string; particion: Particion;
  metricas: Metricas | null; entrenado_en: string;
};

export type Pronostico = {
  id: number; producto_id: number; producto: string;
  cantidad_pronosticada: number | null;
  estado: "DISPONIBLE" | "HISTORIAL_INSUFICIENTE" | "PRODUCTO_NO_CUBIERTO";
};

export type Corrida = {
  id: number; ejecucion_id: number; tipo: "BACKTEST" | "DEMO_PROGRAMADA";
  clave_ejecucion: string; fecha_objetivo: string; estado: string;
  modelo_id: number; version_modelo: string; creado_en: string;
  pronosticos?: Pronostico[];
};

export type ParProducto = {
  producto_id: string; producto?: string; previsto: number; real: number | null;
  diferencia_absoluta: number | null; dentro_mas_menos_20: boolean | null;
  motivo_exclusion?: string;
};

export type EvaluacionDia = {
  fecha_local: string; total_previsto_evaluable: number; total_real_conocido: number;
  productos_evaluables: number; productos_excluidos: number; metricas: Metricas;
  desglose_productos: ParProducto[]; corrida_id?: number;
  pronosticos_no_disponibles?: { producto_id: number; estado: string }[];
};

export type EvaluacionTramo = {
  estado: string; modelo_id: number; version_modelo: string; particion: Particion;
  fecha_inicio: string; fecha_fin: string; fechas_evaluadas: number;
  total_pares_evaluables: number; metricas_globales: Metricas;
  serie_diaria: EvaluacionDia[];
  trazas: { fecha_local: string; corrida_id: number; pronosticos_no_disponibles: { producto_id: number; estado: string }[] }[];
};
