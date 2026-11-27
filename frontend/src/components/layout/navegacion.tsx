/**
 * Mapa único de navegación de FoodSave.
 *
 * Las pantallas se ordenan por las etapas del ciclo del negocio (preparar → pronosticar →
 * planificar → abastecer → vender → evaluar). La barra lateral, las migas, la barra del ciclo
 * y los enlaces «anterior / siguiente» se generan desde esta lista: no duplicar rutas en otros
 * archivos. Cambiar el orden aquí cambia el recorrido sugerido en toda la aplicación.
 */
import type { ReactNode } from "react";

export type NombreIcono =
  | "inicio" | "datos" | "producto" | "ingrediente" | "receta" | "pronostico" | "automatizacion"
  | "plan" | "operacion" | "proveedor" | "pedido" | "inventario" | "venta" | "promocion" | "tienda"
  | "evaluacion" | "reporte" | "configuracion" | "usuarios" | "avisos" | "menu" | "plegar" | "sol"
  | "luna" | "salir" | "chevron" | "guia" | "chispa" | "mano" | "flecha-derecha" | "flecha-izquierda" | "check" | "alerta" | "reloj";

export type Pantalla = { href: string; texto: string; icono: NombreIcono; ayuda: string; soloAdmin?: boolean };
export type Etapa = {
  id: string;
  /** Número visible del paso en el ciclo; las secciones sin número no forman parte del recorrido. */
  numero?: number;
  titulo: string;
  resumen: string;
  /** Color de acento de la etapa (variable CSS del sistema de diseño). */
  color: string;
  pantallas: Pantalla[];
};

export const INICIO: Pantalla = { href: "/", texto: "Resumen", icono: "inicio", ayuda: "Estado del ciclo y siguiente paso." };
export const GUIA: Pantalla = { href: "/como-funciona", texto: "Cómo funciona", icono: "guia", ayuda: "Infografía del flujo completo del negocio." };

export const ETAPAS: Etapa[] = [
  {
    id: "preparar", numero: 1, titulo: "Preparar", resumen: "Carga ventas, catálogo y recetas.", color: "var(--ma-azul)",
    pantallas: [
      { href: "/inicializacion", texto: "Datos iniciales", icono: "datos", ayuda: "Primera carga de ventas, catálogo y stock." },
      { href: "/productos", texto: "Productos", icono: "producto", ayuda: "Catálogo y precios de venta." },
      { href: "/ingredientes", texto: "Ingredientes", icono: "ingrediente", ayuda: "Insumos y unidades de medida." },
      { href: "/recetas", texto: "Recetas", icono: "receta", ayuda: "Cuánto insumo usa cada producto." },
    ],
  },
  {
    id: "pronosticar", numero: 2, titulo: "Pronosticar", resumen: "Entrena el modelo y estima la demanda.", color: "var(--ma-cian)",
    pantallas: [
      { href: "/pronosticos", texto: "Pronósticos y modelos", icono: "pronostico", ayuda: "Versiones del modelo y previsión por producto." },
    ],
  },
  {
    id: "planificar", numero: 3, titulo: "Planificar y producir", resumen: "Convierte el pronóstico en producción e insumos.", color: "var(--ma-amarillo)",
    pantallas: [
      { href: "/automatizaciones", texto: "Automatización", icono: "automatizacion", ayuda: "Programa el ciclo automático y revisa ejecuciones." },
      { href: "/planificacion", texto: "Planes y faltantes", icono: "plan", ayuda: "Cuánto producir y qué falta comprar." },
      { href: "/operaciones", texto: "Operación diaria", icono: "operacion", ayuda: "Tandas, recepciones y vigilancia del stock." },
    ],
  },
  {
    id: "abastecer", numero: 4, titulo: "Abastecer", resumen: "Pide faltantes y recibe mercadería.", color: "var(--ma-verde)",
    pantallas: [
      { href: "/proveedores", texto: "Proveedores y Telegram", icono: "proveedor", ayuda: "Ofertas, conversiones y destinos de envío." },
      { href: "/compras", texto: "Pedidos y envíos", icono: "pedido", ayuda: "Aprobación, envío y recepción de pedidos." },
      { href: "/inventario", texto: "Inventario", icono: "inventario", ayuda: "Saldos por lote y vida útil." },
    ],
  },
  {
    id: "vender", numero: 5, titulo: "Vender", resumen: "Registra ventas y mueve excedentes.", color: "var(--ma-rojo)",
    pantallas: [
      { href: "/ventas", texto: "Caja e historial", icono: "venta", ayuda: "Tickets del día y cierres." },
      { href: "/promociones", texto: "Promociones sugeridas", icono: "promocion", ayuda: "Descuentos propuestos por lote." },
      { href: "/tienda-admin", texto: "Publicar en tienda", icono: "tienda", ayuda: "Catálogo y promociones de la tienda en línea." },
    ],
  },
  {
    id: "evaluar", numero: 6, titulo: "Evaluar", resumen: "Compara pronóstico y venta real.", color: "var(--ma-azul-oscuro)",
    pantallas: [
      { href: "/panel", texto: "Evaluación histórica", icono: "evaluacion", ayuda: "Error del modelo y cobertura." },
      { href: "/informes", texto: "Reportes", icono: "reporte", ayuda: "Ventas, pronósticos y pedidos exportables." },
    ],
  },
  {
    id: "administracion", titulo: "Administración", resumen: "Comercio, cuentas y avisos.", color: "var(--ma-gris)",
    pantallas: [
      { href: "/configuracion", texto: "Configuración", icono: "configuracion", ayuda: "Datos del comercio y modo de envío." },
      { href: "/usuarios", texto: "Usuarios", icono: "usuarios", ayuda: "Cuentas y roles.", soloAdmin: true },
      { href: "/notificaciones", texto: "Notificaciones", icono: "avisos", ayuda: "Incidencias y respuestas de proveedores." },
    ],
  },
];

export const ETAPAS_CICLO = ETAPAS.filter((etapa) => etapa.numero !== undefined);

export function coincide(ruta: string, href: string) {
  return ruta === href || (href !== "/" && ruta.startsWith(`${href}/`));
}

export function visibles(etapa: Etapa, esAdmin: boolean) {
  return etapa.pantallas.filter((pantalla) => !pantalla.soloAdmin || esAdmin);
}

/** Etapa y pantalla de la ruta actual; `null` en Inicio o en rutas fuera del mapa. */
export function ubicar(ruta: string): { etapa: Etapa; pantalla: Pantalla } | null {
  for (const etapa of ETAPAS) {
    const pantalla = etapa.pantallas.find((p) => coincide(ruta, p.href));
    if (pantalla) return { etapa, pantalla };
  }
  return null;
}

/** Pantalla anterior y siguiente dentro del recorrido numerado (sin Administración). */
export function vecinos(ruta: string): { anterior: Pantalla | null; siguiente: Pantalla | null } {
  const recorrido = [INICIO, ...ETAPAS_CICLO.flatMap((etapa) => etapa.pantallas)];
  const indice = recorrido.findIndex((p) => p.href === "/" ? ruta === "/" : coincide(ruta, p.href));
  if (indice < 0) return { anterior: null, siguiente: null };
  return { anterior: recorrido[indice - 1] ?? null, siguiente: recorrido[indice + 1] ?? null };
}

const TRAZOS: Record<NombreIcono, ReactNode> = {
  inicio: <><path d="m3 10 9-7 9 7" /><path d="M5 9v12h14V9" /><path d="M9 21v-7h6v7" /></>,
  datos: <><ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5" /><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" /></>,
  producto: <><path d="m21 16-9 5-9-5V8l9-5 9 5v8Z" /><path d="m3.3 7.5 8.7 5 8.7-5M12 22V12.5" /></>,
  ingrediente: <><path d="M12 22V8" /><path d="M12 8c0-3 2-5 5-5 0 3-2 5-5 5Z" /><path d="M12 13c0-3-2-5-5-5 0 3 2 5 5 5Z" /><path d="M12 18c0-3 2-5 5-5 0 3-2 5-5 5Z" /></>,
  receta: <><path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2Z" /><path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7Z" /></>,
  pronostico: <><path d="m3 17 6-6 4 4 8-8" /><path d="M14 7h7v7" /></>,
  automatizacion: <><rect x="4" y="8" width="16" height="12" rx="2" /><path d="M12 8V4H8M2 14h2M20 14h2M15 13v2M9 13v2" /></>,
  plan: <><rect x="8" y="2" width="8" height="4" rx="1" /><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2M9 12h6M9 16h4" /></>,
  operacion: <><rect x="3" y="4" width="18" height="18" rx="2" /><path d="M8 2v4M16 2v4M3 10h18M12 14v3l2 1" /></>,
  proveedor: <><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2M15 18H9M19 18h2a1 1 0 0 0 1-1v-3.6a1 1 0 0 0-.2-.6l-3.5-4.4A1 1 0 0 0 17.5 8H14" /><circle cx="7" cy="18" r="2" /><circle cx="17" cy="18" r="2" /></>,
  pedido: <><path d="M22 2 11 13" /><path d="m22 2-7 20-4-9-9-4 20-7Z" /></>,
  inventario: <><path d="M22 8.4V20a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8.4a2 2 0 0 1 1.3-1.9l8-3.2a2 2 0 0 1 1.4 0l8 3.2A2 2 0 0 1 22 8.4Z" /><path d="M6 22V10h12v12M6 14h12M6 18h12" /></>,
  venta: <><path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z" /><path d="M8 8h8M8 12h8M8 16h5" /></>,
  promocion: <><path d="M12.6 2.6A2 2 0 0 0 11.2 2H4a2 2 0 0 0-2 2v7.2a2 2 0 0 0 .6 1.4l8.7 8.7a2.4 2.4 0 0 0 3.4 0l6.6-6.6a2.4 2.4 0 0 0 0-3.4Z" /><circle cx="7.5" cy="7.5" r="1" /></>,
  tienda: <><path d="m3 9 1.5-5h15L21 9" /><path d="M3 9v11h18V9M3 9h18M9 20v-6h6v6" /></>,
  evaluacion: <><path d="M3 3v18h18" /><path d="m7 14 4-4 4 4 5-6" /></>,
  reporte: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" /><path d="M14 2v6h6M8 13h8M8 17h5" /></>,
  configuracion: <><path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6" /></>,
  usuarios: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8" /></>,
  avisos: <><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" /><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0" /></>,
  menu: <path d="M4 6h16M4 12h16M4 18h16" />,
  plegar: <><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M9 3v18M16 10l-2 2 2 2" /></>,
  sol: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></>,
  luna: <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />,
  salir: <><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><path d="m16 17 5-5-5-5M21 12H9" /></>,
  chevron: <path d="m6 9 6 6 6-6" />,
  guia: <><circle cx="12" cy="12" r="9" /><path d="m15.5 8.5-2 5-5 2 2-5 5-2Z" /></>,
  chispa: <><path d="M12 3l1.8 4.7 4.7 1.8-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8Z" /><path d="m19 15 .8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8Z" /></>,
  mano: <><path d="M18 11V6a2 2 0 0 0-4 0v5M14 10V4a2 2 0 0 0-4 0v6M10 10.5V6a2 2 0 0 0-4 0v8" /><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.9-6-2.4l-3.6-3.6a2 2 0 0 1 2.8-2.8L7 15" /></>,
  "flecha-derecha": <path d="M5 12h14m-6-6 6 6-6 6" />,
  "flecha-izquierda": <path d="M19 12H5m6 6-6-6 6-6" />,
  check: <path d="m5 12 5 5L20 7" />,
  alerta: <><path d="M12 9v4M12 17h.01" /><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" /></>,
  reloj: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
};

/** Íconos de trazo estilo Lucide; siempre decorativos, el texto acompaña cada uno. */
export function Icono({ nombre, tamano = 20 }: { nombre: NombreIcono; tamano?: number }) {
  return <svg className="ma-icon" width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">{TRAZOS[nombre]}</svg>;
}
