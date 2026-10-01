/** Etiquetas de presentación. No modifica los estados ni las decisiones de la API. */
const etiquetas: Record<string, string> = {
  PENDIENTE: "En espera", EN_EJECUCION: "En curso", COMPLETADA: "Completada", COMPLETADO: "Completado", FALLIDA: "Requiere revisión", REINTENTANDO: "Reintento programado",
  CALCULADAS: "Ingredientes calculados", INCOMPLETAS: "Faltan datos para calcular", PENDIENTE_M03: "Ingredientes pendientes de cálculo",
  GENERADA: "Lista para revisar", BLOQUEADA: "Requiere corrección", SIN_FALTANTES: "Stock suficiente", CANCELADA: "Cancelada", PENDIENTE_GENERACION: "Pedidos aún sin generar",
  DISPONIBLE: "Disponible", LISTO: "Listo", ENTRENANDO: "Preparando modelo", EVALUANDO: "Evaluando modelo", EVALUADO: "Evaluado", PARCIAL: "Resultado parcial",
  HISTORIAL_INSUFICIENTE: "No hay suficiente historial", PRODUCTO_NO_CUBIERTO: "Producto fuera del modelo", CALCULADO: "Calculado",
  PREPARAR_MODELO: "Preparar modelo", EVALUAR_MODELO: "Evaluar modelo", GENERAR_PROPUESTA: "Generar plan y pedidos", EVALUAR_PRONOSTICO: "Comparar pronóstico y venta", EVALUAR_PROMOCION: "Evaluar sugerencia de promoción",
  BACKTEST: "Evaluación histórica", DEMO: "Escenario de demostración", DEMOSTRACION: "Escenario de demostración", DIARIO: "Pronóstico diario", MANUAL: "Solicitud manual",
  PROGRAMADA: "Programada", DESPACHADA: "Enviada a ejecución", DATOS_CARGADOS: "Datos cargados", MODELO_LISTO: "Modelo listo",
};
export function etiquetaDato(valor: string): string { return etiquetas[valor] ?? valor.replaceAll("_", " ").toLocaleLowerCase("es"); }
export function decimalLegible(valor: string): string {
  const [entero, decimal] = valor.split(".");
  const fraccion = decimal?.replace(/0+$/, "");
  return fraccion ? `${entero},${fraccion}` : entero;
}
