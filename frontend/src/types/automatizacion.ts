export type TipoAutomatizacion =
  | "PREPARAR_MODELO"
  | "EVALUAR_MODELO"
  | "GENERAR_PROPUESTA"
  | "EVALUAR_PRONOSTICO"
  | "EVALUAR_PROMOCION";

export type EstadoProgramacion = "PROGRAMADA" | "DESPACHADA" | "CANCELADA";
export type EstadoEjecucion = "PENDIENTE" | "EN_EJECUCION" | "REINTENTANDO" | "COMPLETADA" | "FALLIDA";
export type EstadoIntento = "EN_EJECUCION" | "COMPLETADA" | "FALLIDA";

export type ProgramacionDemo = {
  id: number;
  tipo: "GENERAR_PROPUESTA" | "EVALUAR_PROMOCION";
  estado: EstadoProgramacion;
  ejecutar_desde_utc: string;
  fecha_hora_simulada_local: string;
  parametros: { fecha_objetivo_demo?: string; producto_ids?: number[]; [clave: string]: unknown };
  clave_idempotencia: string;
  despachada_en: string | null;
  lease_hasta: string | null;
  creado_por: number | null;
  creado_en: string;
  ejecucion_id: number | null;
};

export type CrearProgramacionDemo = {
  tipo: "GENERAR_PROPUESTA";
  ejecutar_desde_utc: string;
  fecha_hora_simulada_local: string;
  fecha_objetivo_demo: string;
  producto_ids: number[];
  clave_idempotencia: string;
};

export type IntentoAutomatizacion = {
  id: number;
  numero_intento: number;
  inicio_en: string;
  fin_en: string | null;
  estado: EstadoIntento;
  mensaje_error: string | null;
};

export type EjecucionAutomatizacion = {
  id: number;
  programacion_id: number | null;
  tipo: TipoAutomatizacion;
  clave_idempotencia: string;
  huella_entrada: string;
  datos_entrada: Record<string, unknown>;
  estado: EstadoEjecucion;
  inicio_en: string | null;
  fin_en: string | null;
  proximo_intento_en: string | null;
  datos_salida: Record<string, unknown> | null;
  mensaje_error: string | null;
  intentos: IntentoAutomatizacion[];
};
