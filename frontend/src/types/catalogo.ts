export type Producto = {
  id: number;
  codigo: string;
  nombre: string;
  demostrar: boolean;
  activo: boolean;
  origen: string | null;
  sku_externo: string | null;
};

export type VentaDiaria = {
  id: number;
  producto_id: number;
  producto: string;
  sku_externo: string | null;
  /** Fecha local `YYYY-MM-DD`, no un instante UTC. */
  fecha_local: string;
  unidades_vendidas: number;
  revision_actual: number;
  actualizado_en: string | null;
};

export type RevisionVenta = {
  id: number;
  numero_revision: number;
  unidades_vendidas: number;
  origen_cambio: string;
  motivo: string;
  usuario_id: number | null;
  importacion_id: number | null;
  creado_en: string | null;
};

export type CorreccionVenta = {
  venta_id: number;
  revision_venta_id: number;
  revision_actual: number;
  unidades_vendidas: number;
};
