export type EstadoInicializacion =
  | "PENDIENTE"
  | "DATOS_CARGADOS"
  | "ENTRENANDO"
  | "MODELO_LISTO"
  | "FALLIDA";

export type ConfiguracionInicial = {
  estado: EstadoInicializacion;
  huella_ventas: string | null;
  huella_catalogo: string | null;
  huella_solicitud: string | null;
  fecha_objetivo_demo: string | null;
  fecha_referencia_stock: string | null;
  iniciada_en: string | null;
  completada_en: string | null;
  mensaje_error: string | null;
  preparacion_modelo: PreparacionModelo | null;
};

export type PreparacionModelo = {
  ejecucion_id: number;
  estado: "PENDIENTE" | "EN_EJECUCION" | "REINTENTANDO" | "COMPLETADA" | "FALLIDA";
  version_modelo: string;
  modelo_id: number | null;
  mensaje_error: string | null;
};

export type ErrorEntrada = { campo: string; mensaje: string };

export type ProductoDemo = { codigo: string; nombre: string; sku_externo: string };

export type VistaPrevia = {
  aceptable: boolean;
  total_errores: number;
  errores: ErrorEntrada[];
  filas_por_hoja: Record<string, number>;
  ventas: {
    filas: number;
    skus: number;
    primera_fecha: string | null;
    ultima_fecha: string | null;
  };
  catalogo: {
    productos: number;
    productos_demo: ProductoDemo[];
    ingredientes: number;
    lineas_receta: number;
    filas_stock: number;
  };
  huellas: { ventas: string; catalogo: string; solicitud: string };
  /** Solo cuando la entrega trae el CSV de tickets del piloto. */
  adaptador_bakery?: {
    lineas_leidas: number;
    lineas_negativas_excluidas: number;
    lineas_invalidas: number;
    pares_generados: number;
    articulos: number;
  };
};

export type InformeCarga = {
  estado: EstadoInicializacion;
  ya_estaba_cargada: boolean;
  productos: number;
  ventas_diarias: number;
  importacion_id: number;
  ingredientes: number;
  lineas_receta: number;
  movimientos_apertura: number;
  /** Dominios que aún no tienen servicio; la instalación no queda inicializada. */
  pendiente_de: string[];
  ejecucion_id: number | null;
};

export type ResultadoCargaPiloto = {
  importacion_id: number;
  repetida: boolean;
  productos: number;
  filas_aceptadas: number;
  filas_negativas_excluidas: number;
  ventas_diarias_creadas: number;
  version_modelo: string;
  ejecucion_id: number;
  estado_ejecucion: string;
};
