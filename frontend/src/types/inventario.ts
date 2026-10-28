export type TipoItem = "producto" | "ingrediente";

/** Producto: OPTIMO (días 1–3), PRIORIDAD (4–5), MERMA (6+). Ingrediente: VIGENTE/VENCIDO. */
export type EstadoLote = "OPTIMO" | "PRIORIDAD" | "MERMA" | "VIGENTE" | "VENCIDO" | "DESCONOCIDO";

export type LoteDisponible = {
  lote_id: number;
  codigo_lote: string;
  lote_informado: boolean;
  fecha_caducidad: string | null;
  fecha_limite_venta: string | null;
  fecha_ingreso?: string | null;
  saldo: string;
  estado: EstadoLote;
  dia_de_vida: number | null;
  cuenta: boolean;
  motivo: string;
};

export type DisponibilidadItem = {
  tipo: TipoItem;
  item_id: number;
  codigo: string;
  nombre: string;
  unidad: string;
  stock_conocido: boolean;
  /** `null` si no hay ningún lote: desconocido, no cero. */
  cantidad_disponible: string | null;
  cantidad_prioridad: string;
  cantidad_excluida: string;
  vigencia_desconocida: boolean;
  lotes: LoteDisponible[];
};

export type MetaDisponibilidad = {
  fecha: string;
  leido_en: string;
  huella: string;
  vida_maxima_producto_dias: number;
  ultimo_dia_optimo: number;
};

export type Movimiento = {
  id: number;
  tipo: TipoItem;
  lote_id: number;
  codigo_lote: string;
  item_nombre: string;
  tipo_movimiento: "APERTURA" | "AJUSTE" | "RECEPCION" | "VENTA" | "ANULA_VENTA" | "ENTRADA";
  delta: string;
  saldo_resultante: string;
  motivo: string;
  clave_operacion: string;
  usuario_id: number | null;
  efectivo_en_demo: string;
  creado_en: string | null;
};

export type SolicitudAjuste = {
  tipo: TipoItem;
  lote_id: number;
  delta: string;
  motivo: string;
  clave_operacion: string;
  /** Hora local del escenario, sin zona: `YYYY-MM-DDTHH:mm:00`. */
  efectivo_en_demo: string;
};

export type ResultadoAjuste = {
  movimiento_id: number;
  tipo: TipoItem;
  lote_id: number;
  tipo_movimiento: string;
  delta: string;
  saldo_resultante: string;
  efectivo_en_demo: string;
  repetido: boolean;
  evaluacion_promocion_ejecucion_id?: number | null;
};

export type ContextoEntradas = {
  fecha_actual: string; zona_horaria: string; vida_maxima_dias: number;
  productos: { id: number; codigo: string; nombre: string; activo: boolean }[];
};
export type LineaEntrada = {
  producto_id: number; codigo_lote: string; cantidad: number;
  fecha_elaboracion: string; fecha_caducidad: string; fecha_limite_venta: string;
};
export type SolicitudEntrada = {
  clave_operacion: string; fecha_entrada: string; motivo: string; lineas: LineaEntrada[];
};
export type ResumenEntrada = {
  id: number; numero: string; fecha_entrada: string; motivo: string;
  usuario_id: number; nombre_usuario: string; creado_en: string; lotes?: number; unidades?: number;
};
export type DetalleEntrada = ResumenEntrada & {
  lineas: (LineaEntrada & { id: number; lote_id: number; movimiento_id: number; codigo_producto: string; nombre_producto: string })[];
};
