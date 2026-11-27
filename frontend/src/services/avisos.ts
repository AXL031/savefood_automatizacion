/**
 * Avisos emergentes (arriba a la derecha) para el resultado de cada operación.
 *
 * `http.ts` publica aquí los errores de conexión/servidor y el resultado de toda operación que
 * cambia datos (POST, PATCH, PUT, DELETE). Las pantallas pueden llamar a `notificar` para avisos
 * propios. El contenedor visual vive en `components/ui/Avisos.tsx` y escucha este evento.
 */
export type TonoAviso = "error" | "exito" | "advertencia" | "info";
export type Aviso = { tono: TonoAviso; titulo: string; mensaje?: string; ayuda?: string; duracion?: number };

export const EVENTO_AVISO = "foodsave:aviso";

/** Nunca lanza: un aviso que no se puede mostrar no debe cambiar el resultado de la operación. */
export function notificar(aviso: Aviso): void {
  if (typeof window === "undefined" || typeof window.CustomEvent !== "function") return;
  try {
    window.dispatchEvent(new window.CustomEvent<Aviso>(EVENTO_AVISO, { detail: aviso }));
  } catch {
    // Entornos sin eventos del DOM (pruebas, SSR): se omite el aviso.
  }
}

/** Qué hacer según el código HTTP: frases cortas para alguien sin conocimientos técnicos. */
export function ayudaPorEstado(status: number): string {
  if (status === 0) return "Comprueba que FoodSave siga encendido (Docker) y tu conexión. Luego vuelve a intentarlo.";
  if (status === 400 || status === 422) return "Revisa los datos marcados en el formulario y corrígelos.";
  if (status === 403) return "Tu cuenta no tiene permiso. Pide ayuda a un administrador.";
  if (status === 404) return "El registro ya no existe. Actualiza la pantalla.";
  if (status === 409) return "Otro cambio llegó antes. Actualiza la pantalla y repite la acción.";
  if (status === 413) return "El archivo es demasiado grande. Usa uno más liviano.";
  if (status === 429) return "Demasiados intentos seguidos. Espera unos segundos.";
  if (status >= 500) return "Falla del servidor. Espera un momento y reintenta; si se repite, avisa al responsable.";
  return "Vuelve a intentarlo. Si el problema sigue, actualiza la pantalla.";
}

const EXITOS: [RegExp, string][] = [
  [/\/vista-previa$/, "Archivos validados"],
  [/\/inicializacion\/confirmar$/, "Carga confirmada"],
  [/\/piloto-bakery$/, "Carga piloto enviada"],
  [/\/reintentar-preparacion$/, "Preparación reintentada"],
  [/\/preparar-modelo$/, "Entrenamiento iniciado"],
  [/\/comprobar$/, "Comprobación terminada"],
  [/\/programar$/, "Automatización programada"],
  [/\/pedidos\/generar$/, "Pedidos generados"],
  [/\/aprobar$/, "Pedido aprobado"],
  [/\/rechazar$/, "Pedido rechazado"],
  [/\/reintentar$/, "Reintento enviado"],
  [/\/cancelar$/, "Propuesta cancelada"],
  [/\/corregir$/, "Corrección guardada"],
  [/\/conciliar$/, "Pedido conciliado"],
  [/\/recepciones$/, "Recepción registrada"],
  [/\/verificar-destinos?$/, "Destino verificado"],
  [/\/mensajes?-prueba$/, "Mensaje de prueba enviado"],
  [/\/anular$/, "Ticket anulado"],
  [/\/ventas\/cierres$/, "Cierre del día registrado"],
  [/\/ventas\/tickets$/, "Ticket registrado"],
  [/\/ventas\/cotizaciones$/, "Cotización calculada"],
  [/\/inventario\/ajustes$/, "Ajuste de stock registrado"],
  [/\/entradas-productos/, "Entrada de productos registrada"],
  [/\/promociones\/regla$/, "Regla de promoción guardada"],
  [/\/gestionar$/, "Programación actualizada"],
  [/\/usuarios/, "Usuario guardado"],
  [/\/ofertas/, "Oferta guardada"],
  [/\/proveedores/, "Proveedor actualizado"],
  [/\/ingredientes/, "Ingrediente guardado"],
  [/\/recetas/, "Receta guardada"],
  [/\/productos/, "Producto guardado"],
  [/\/negocios/, "Datos del comercio guardados"],
  [/\/configuracion$/, "Configuración guardada"],
];

/** Operaciones que no merecen aviso de éxito (la pantalla ya cambia de estado o es un acceso). */
const SIN_AVISO_EXITO = [/\/autenticacion\//];

export function tituloExito(ruta: string, metodo: string): string | null {
  const limpia = ruta.split("?")[0];
  if (SIN_AVISO_EXITO.some((patron) => patron.test(limpia))) return null;
  const coincidencia = EXITOS.find(([patron]) => patron.test(limpia));
  if (coincidencia) return coincidencia[1];
  return metodo === "DELETE" ? "Eliminado correctamente" : metodo === "POST" ? "Operación completada" : "Cambios guardados";
}
