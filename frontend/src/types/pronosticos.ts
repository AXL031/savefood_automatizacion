/**
 * Tipos TypeScript para el dominio de pronósticos y evaluación histórica (K03 / K04).
 * Coincide estrictamente con los contratos de POLITICA_EVALUACION.md y CONTRATO_ARTEFACTO_INFERENCIA.md.
 */

export interface MetricasEvaluacion {
  total_pronosticados: number;
  pares_evaluables: number;
  productos_excluidos: number;
  cobertura_pct: number;
  mae: number | null;
  wape_pct: number | null;
  dentro_mas_menos_20_pct: number | null;
  dentro_mas_menos_10_pct: number | null;
  suma_errores_absolutos: number;
  suma_reales: number;
}

export interface DesgloseProducto {
  producto_id: string;
  previsto: number;
  real: number | null;
  diferencia_absoluta: number | null;
  dentro_mas_menos_20: boolean | null;
  motivo_exclusion?: string;
}

export interface EvaluacionDia {
  fecha_local: string;
  total_previsto_evaluable: number;
  total_real_conocido: number;
  productos_evaluables: number;
  productos_excluidos: number;
  metricas: MetricasEvaluacion;
  desglose_productos: DesgloseProducto[];
}

export interface ParticionInfo {
  version_politica: string;
  inicio_entrenamiento: string;
  fin_entrenamiento: string;
  inicio_validacion: string;
  fin_validacion: string;
  inicio_prueba: string;
  fin_prueba: string;
  meses_validos: number;
  meses_validacion: number;
  meses_prueba: number;
}

export interface EvaluacionTramoCompleto {
  estado: string; // "demostracion_historica"
  version_modelo: string;
  fecha_inicio: string;
  fecha_fin: string;
  fechas_evaluadas: number;
  total_pares_evaluables: number;
  metricas_globales: MetricasEvaluacion;
  serie_diaria: EvaluacionDia[];
  particion?: ParticionInfo;
}

export interface ItemPronostico {
  producto_id: string;
  unidades_pronosticadas: number | null;
  motivo_no_disponible?: "HISTORIAL_INSUFICIENTE" | "PRODUCTO_NO_CUBIERTO" | null;
}

export interface CorridaPronostico {
  id: string;
  fecha_ejecucion_utc: string;
  fecha_objetivo_demo: string;
  version_modelo: string;
  estado: "PENDIENTE" | "EN_EJECUCION" | "COMPLETADA" | "FALLIDA";
  pronosticos: ItemPronostico[];
}
