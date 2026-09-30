/** Cantidades decimales viajan como texto con 3 decimales para no perder precisión. */
export type UnidadBase = "g" | "kg" | "ml" | "l" | "unidad";

export type Ingrediente = {
  id: number;
  codigo: string;
  nombre: string;
  unidad_base: UnidadBase;
  activo: boolean;
  en_uso: boolean;
  lineas_receta: number;
  lotes: number;
  /** Falso cuando una receta o un lote ya usan la unidad: el servidor rechaza el cambio. */
  unidad_editable: boolean;
};

export type NuevoIngrediente = { codigo: string; nombre: string; unidad_base: UnidadBase };
export type CambioIngrediente = Partial<{ nombre: string; unidad_base: UnidadBase; activo: boolean }>;

export type LineaReceta = {
  ingrediente_id: number;
  codigo: string;
  nombre: string;
  unidad_base: UnidadBase;
  cantidad_por_unidad: string;
};

export type RecetaVersion = {
  receta_id: number;
  producto_id: number;
  version: number;
  activo: boolean;
  motivo: string | null;
  creado_en: string | null;
  lineas: LineaReceta[];
};

export type ProductoConReceta = {
  producto_id: number;
  producto_codigo: string;
  producto_nombre: string;
  demostrar: boolean;
  receta: RecetaVersion | null;
};

export type NuevaVersionReceta = {
  motivo: string;
  lineas: { ingrediente_id: number; cantidad_por_unidad: string }[];
};
