export type TipoItem = "producto" | "ingrediente";

/** Producto: OPTIMO (días 1–3), PRIORIDAD (4–5), MERMA (6+). Ingrediente: VIGENTE/VENCIDO. */
export type EstadoLote = "OPTIMO" | "PRIORIDAD" | "MERMA" | "VIGENTE" | "VENCIDO" | "DESCONOCIDO";

export type LoteDisponible = {
  lote_id: number;
  codigo_lote: string;
  lote_informado: boolean;
  fecha_caducidad: string | null;
  fecha_limite_venta: string | null;
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
  tipo_movimiento: "APERTURA" | "AJUSTE";
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
};
