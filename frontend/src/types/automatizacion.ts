export type EstadoEjecucion =
  | "PENDIENTE"
  | "EN_EJECUCION"
  | "VERIFICANDO"
  | "COMPLETADO"
  | "REINTENTANDO"
  | "FALLIDO"
  | "CANCELADO";

export type TipoAutomatizacion =
  | "PLANIFICACION_DIARIA"
  | "PEDIDO_PROVEEDOR"
  | "SEGUIMIENTO_EXCEDENTES"
  | "ACTIVACION_PROMOCION"
  | "SEGUIMIENTO_PROMOCION";

export type Automatizacion = {
  id: number;
  nombre: string;
  tipo: TipoAutomatizacion;
  habilitado: boolean;
  programacion: string;
  maximo_reintentos: number;
};

export type IntentoAutomatizacion = {
  id: number;
  numero_intento: number;
  estado: EstadoEjecucion;
  inicio_en: string;
  fin_en: string | null;
  mensaje_error: string | null;
};

export type EjecucionAutomatizacion = {
  id: number;
  automatizacion_id: number;
  nombre_automatizacion?: string;
  estado: EstadoEjecucion;
  inicio_en: string | null;
  fin_en: string | null;
  mensaje_error: string | null;
  cantidad_reintentos: number;
  intentos?: IntentoAutomatizacion[];
  datos_entrada?: Record<string, unknown> | null;
  datos_salida?: Record<string, unknown> | null;
};
