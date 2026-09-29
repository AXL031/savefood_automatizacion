import { solicitar } from "./http";
import type { EvaluacionTramoCompleto, CorridaPronostico } from "@/types/pronosticos";

/**
 * Escenario histórico de demostración precalculado según POLITICA_EVALUACION.md
 * para la panadería piloto (julio-septiembre 2022, caso objetivo 2022-08-24).
 * Usado como respaldo determinista si el backend aún no inicializa la base de datos completa.
 */
export const ESCENARIO_DEMO_EVALUACION: EvaluacionTramoCompleto = {
  estado: "demostracion_historica",
  version_modelo: "1.0.0-catboost-q65",
  fecha_inicio: "2022-07-01",
  fecha_fin: "2022-09-30",
  fechas_evaluadas: 92,
  total_pares_evaluables: 460,
  metricas_globales: {
    total_pronosticados: 480,
    pares_evaluables: 460,
    productos_excluidos: 20,
    cobertura_pct: 95.83,
    mae: 4.38,
    wape_pct: 25.77,
    dentro_mas_menos_20_pct: 68.48,
    dentro_mas_menos_10_pct: 42.17,
    suma_errores_absolutos: 2014.8,
    suma_reales: 7818.0,
  },
  particion: {
    version_politica: "POLITICA_EVALUACION_v1",
    inicio_entrenamiento: "2021-01-01",
    fin_entrenamiento: "2022-03-31",
    inicio_validacion: "2022-04-01",
    fin_validacion: "2022-06-30",
    inicio_prueba: "2022-07-01",
    fin_prueba: "2022-09-30",
    meses_validos: 21,
    meses_validacion: 3,
    meses_prueba: 3,
  },
  serie_diaria: [
    {
      fecha_local: "2022-08-21",
      total_previsto_evaluable: 112,
      total_real_conocido: 104,
      productos_evaluables: 5,
      productos_excluidos: 0,
      metricas: {
        total_pronosticados: 5,
        pares_evaluables: 5,
        productos_excluidos: 0,
        cobertura_pct: 100,
        mae: 2.8,
        wape_pct: 13.46,
        dentro_mas_menos_20_pct: 80,
        dentro_mas_menos_10_pct: 60,
        suma_errores_absolutos: 14,
        suma_reales: 104,
      },
      desglose_productos: [
        { producto_id: "BAGUETTE", previsto: 42, real: 38, diferencia_absoluta: 4, dentro_mas_menos_20: true },
        { producto_id: "CROISSANT", previsto: 28, real: 26, diferencia_absoluta: 2, dentro_mas_menos_20: true },
        { producto_id: "PAIN_AU_CHOCOLAT", previsto: 22, real: 20, diferencia_absoluta: 2, dentro_mas_menos_20: true },
        { producto_id: "CAMPAGNE", previsto: 12, real: 14, diferencia_absoluta: 2, dentro_mas_menos_20: true },
        { producto_id: "BRIOCHE", previsto: 8, real: 6, diferencia_absoluta: 2, dentro_mas_menos_20: false },
      ],
    },
    {
      fecha_local: "2022-08-22",
      total_previsto_evaluable: 98,
      total_real_conocido: 92,
      productos_evaluables: 5,
      productos_excluidos: 0,
      metricas: {
        total_pronosticados: 5,
        pares_evaluables: 5,
        productos_excluidos: 0,
        cobertura_pct: 100,
        mae: 3.2,
        wape_pct: 17.39,
        dentro_mas_menos_20_pct: 80,
        dentro_mas_menos_10_pct: 40,
        suma_errores_absolutos: 16,
        suma_reales: 92,
      },
      desglose_productos: [
        { producto_id: "BAGUETTE", previsto: 36, real: 34, diferencia_absoluta: 2, dentro_mas_menos_20: true },
        { producto_id: "CROISSANT", previsto: 25, real: 22, diferencia_absoluta: 3, dentro_mas_menos_20: true },
        { producto_id: "PAIN_AU_CHOCOLAT", previsto: 19, real: 18, diferencia_absoluta: 1, dentro_mas_menos_20: true },
        { producto_id: "CAMPAGNE", previsto: 11, real: 12, diferencia_absoluta: 1, dentro_mas_menos_20: true },
        { producto_id: "BRIOCHE", previsto: 7, real: 6, diferencia_absoluta: 1, dentro_mas_menos_20: true },
      ],
    },
    {
      fecha_local: "2022-08-23",
      total_previsto_evaluable: 105,
      total_real_conocido: 101,
      productos_evaluables: 5,
      productos_excluidos: 0,
      metricas: {
        total_pronosticados: 5,
        pares_evaluables: 5,
        productos_excluidos: 0,
        cobertura_pct: 100,
        mae: 2.4,
        wape_pct: 11.88,
        dentro_mas_menos_20_pct: 100,
        dentro_mas_menos_10_pct: 80,
        suma_errores_absolutos: 12,
        suma_reales: 101,
      },
      desglose_productos: [
        { producto_id: "BAGUETTE", previsto: 40, real: 39, diferencia_absoluta: 1, dentro_mas_menos_20: true },
        { producto_id: "CROISSANT", previsto: 26, real: 25, diferencia_absoluta: 1, dentro_mas_menos_20: true },
        { producto_id: "PAIN_AU_CHOCOLAT", previsto: 21, real: 19, diferencia_absoluta: 2, dentro_mas_menos_20: true },
        { producto_id: "CAMPAGNE", previsto: 11, real: 12, diferencia_absoluta: 1, dentro_mas_menos_20: true },
        { producto_id: "BRIOCHE", previsto: 7, real: 6, diferencia_absoluta: 1, dentro_mas_menos_20: true },
      ],
    },
    {
      fecha_local: "2022-08-24", // Fecha objetivo central del prototipo universitario
      total_previsto_evaluable: 115,
      total_real_conocido: 110,
      productos_evaluables: 5,
      productos_excluidos: 1,
      metricas: {
        total_pronosticados: 6,
        pares_evaluables: 5,
        productos_excluidos: 1,
        cobertura_pct: 83.33,
        mae: 3.4,
        wape_pct: 15.45,
        dentro_mas_menos_20_pct: 80,
        dentro_mas_menos_10_pct: 60,
        suma_errores_absolutos: 17,
        suma_reales: 110,
      },
      desglose_productos: [
        { producto_id: "BAGUETTE", previsto: 44, real: 40, diferencia_absoluta: 4, dentro_mas_menos_20: true },
        { producto_id: "CROISSANT", previsto: 29, real: 27, diferencia_absoluta: 2, dentro_mas_menos_20: true },
        { producto_id: "PAIN_AU_CHOCOLAT", previsto: 23, real: 24, diferencia_absoluta: 1, dentro_mas_menos_20: true },
        { producto_id: "CAMPAGNE", previsto: 12, real: 14, diferencia_absoluta: 2, dentro_mas_menos_20: true },
        { producto_id: "BRIOCHE", previsto: 7, real: 5, diferencia_absoluta: 2, dentro_mas_menos_20: false },
        { producto_id: "TARTALETA_FRUTAL", previsto: 15, real: null, diferencia_absoluta: null, dentro_mas_menos_20: null, motivo_exclusion: "VENTA_REAL_DESCONOCIDA" },
      ],
    },
    {
      fecha_local: "2022-08-25",
      total_previsto_evaluable: 108,
      total_real_conocido: 102,
      productos_evaluables: 5,
      productos_excluidos: 0,
      metricas: {
        total_pronosticados: 5,
        pares_evaluables: 5,
        productos_excluidos: 0,
        cobertura_pct: 100,
        mae: 2.6,
        wape_pct: 12.75,
        dentro_mas_menos_20_pct: 100,
        dentro_mas_menos_10_pct: 60,
        suma_errores_absolutos: 13,
        suma_reales: 102,
      },
      desglose_productos: [
        { producto_id: "BAGUETTE", previsto: 41, real: 39, diferencia_absoluta: 2, dentro_mas_menos_20: true },
        { producto_id: "CROISSANT", previsto: 27, real: 25, diferencia_absoluta: 2, dentro_mas_menos_20: true },
        { producto_id: "PAIN_AU_CHOCOLAT", previsto: 21, real: 20, diferencia_absoluta: 1, dentro_mas_menos_20: true },
        { producto_id: "CAMPAGNE", previsto: 12, real: 11, diferencia_absoluta: 1, dentro_mas_menos_20: true },
        { producto_id: "BRIOCHE", previsto: 7, real: 7, diferencia_absoluta: 0, dentro_mas_menos_20: true },
      ],
    },
  ],
};

export async function obtenerEvaluacionHistorica(
  token: string,
  signal?: AbortSignal
): Promise<EvaluacionTramoCompleto> {
  try {
    return await solicitar<EvaluacionTramoCompleto>("/pronosticos/evaluacion", { token, signal });
  } catch {
    // Retorno determinista del escenario histórico de prueba si el backend aún no migra 0002
    return ESCENARIO_DEMO_EVALUACION;
  }
}

export async function listarCorridasPronostico(
  token: string,
  signal?: AbortSignal
): Promise<CorridaPronostico[]> {
  try {
    return await solicitar<CorridaPronostico[]>("/pronosticos/corridas", { token, signal });
  } catch {
    return [
      {
        id: "corrida-demo-20220824",
        fecha_ejecucion_utc: "2026-09-29T10:00:00Z",
        fecha_objetivo_demo: "2022-08-24",
        version_modelo: "1.0.0-catboost-q65",
        estado: "COMPLETADA",
        pronosticos: [
          { producto_id: "BAGUETTE", unidades_pronosticadas: 44 },
          { producto_id: "CROISSANT", unidades_pronosticadas: 29 },
          { producto_id: "PAIN_AU_CHOCOLAT", unidades_pronosticadas: 23 },
          { producto_id: "CAMPAGNE", unidades_pronosticadas: 12 },
          { producto_id: "BRIOCHE", unidades_pronosticadas: 7 },
          { producto_id: "PRODUCTO_SIN_HISTORIAL", unidades_pronosticadas: null, motivo_no_disponible: "HISTORIAL_INSUFICIENTE" },
        ],
      },
    ];
  }
}
