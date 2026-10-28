/**
 * Datos de ejemplo mientras no existe el backend T01–T04.
 * Solo los usa servicios.ts en modo ejemplo; las pantallas nunca los importan directamente.
 * Las cantidades son internas: el cliente solo ve el estado (contrato T03).
 */
import type { Categoria } from "./tipos";

export const COMERCIO = {
  nombre: "Pastelería Maria Juanita",
  lema: "Pastelería y panadería artesanal",
  ciudad: "Lima, Perú",
  horarios: [
    { dias: "Lunes a Viernes", horas: "07:30 - 20:00" },
    { dias: "Sábados", horas: "08:00 - 21:00" },
    { dias: "Domingos", horas: "08:30 - 18:30" },
  ],
  /** Número y titular ficticios, solo para mostrar el pago simulado. */
  pago_simulado: { numero: "980 112 400", titular: "Pastelería Maria Juanita" },
};

export const UMBRAL_ULTIMAS_UNIDADES = 5;

export const CATEGORIAS: Categoria[] = [
  { codigo: "panes", nombre: "Panes y hojaldres", descripcion: "Masa madre, brioche y laminados", imagen: "/tienda/categorias/panes.jpg" },
  { codigo: "tortas", nombre: "Tortas clásicas", descripcion: "Para celebrar", imagen: "/tienda/categorias/tortas.jpg" },
  { codigo: "kekes", nombre: "Kekes caseros", descripcion: "Recién salidos", imagen: "/tienda/categorias/kekes.jpg" },
  { codigo: "postres-personales", nombre: "Postres personales", descripcion: "Para consentirte", imagen: "/tienda/categorias/postres-personales.jpg" },
  { codigo: "postres-enteros", nombre: "Postres enteros", descripcion: "Para compartir", imagen: "/tienda/categorias/postres-enteros.jpg" },
  { codigo: "bocados", nombre: "Bocados salados", descripcion: "Empanadas y quiches", imagen: "/tienda/categorias/bocados.jpg" },
];

export type ProductoEjemplo = {
  id: number;
  codigo: string;
  nombre: string;
  categoria: string;
  descripcion: string;
  presentacion: string;
  imagen: string;
  precio: string;
  stock: number;
};

export const PRODUCTOS: ProductoEjemplo[] = [
  { id: 1, codigo: "CROISSANT", nombre: "Croissant de Mantequilla", categoria: "panes", descripcion: "Hojaldre laminado a mano con mantequilla, crujiente por fuera y suave por dentro.", presentacion: "90 g · Por unidad", imagen: "/tienda/productos/croissant.jpg", precio: "6.50", stock: 24 },
  { id: 2, codigo: "BAGUETTE", nombre: "Baguette Artesanal", categoria: "panes", descripcion: "Harina de molienda tradicional y fermentación lenta de 24 horas. Corteza dorada.", presentacion: "250 g · Alargada", imagen: "/tienda/productos/baguette.jpg", precio: "6.50", stock: 18 },
  { id: 3, codigo: "CIABATTA", nombre: "Pan Ciabatta", categoria: "panes", descripcion: "Corteza crocante y miga alveolada, elaborado con harina de fuerza, agua y sal.", presentacion: "250 g · Por pieza", imagen: "/tienda/productos/ciabatta.jpg", precio: "4.50", stock: 30 },
  { id: 4, codigo: "BRIOCHE", nombre: "Brioche de Mantequilla", categoria: "panes", descripcion: "Trenza esponjosa con mantequilla y un toque de vainilla.", presentacion: "400 g · Molde", imagen: "/tienda/productos/brioche.jpg", precio: "14.00", stock: 3 },
  { id: 5, codigo: "SELVA_NEGRA", nombre: "Selva Negra", categoria: "tortas", descripcion: "Bizcocho de chocolate, crema chantilly y cerezas.", presentacion: "18 cm · 8 porciones", imagen: "/tienda/productos/selva-negra.jpg", precio: "52.00", stock: 6 },
  { id: 6, codigo: "RED_VELVET", nombre: "Red Velvet", categoria: "tortas", descripcion: "Bizcocho rojo aterciopelado con frosting de queso crema.", presentacion: "20 cm · 10 porciones", imagen: "/tienda/productos/red-velvet.jpg", precio: "55.00", stock: 0 },
  { id: 7, codigo: "TRES_LECHES", nombre: "Torta Tres Leches", categoria: "tortas", descripcion: "Bizcocho esponjoso bañado en tres leches y cubierto con merengue.", presentacion: "Porción individual", imagen: "/tienda/productos/tres-leches.jpg", precio: "22.00", stock: 9 },
  { id: 8, codigo: "TURRON_DONA_PEPA", nombre: "Turrón de Doña Pepa", categoria: "tortas", descripcion: "Varillas con anís bañadas en miel de chancaca y grageas.", presentacion: "500 g · 4-5 porciones", imagen: "/tienda/productos/turron-dona-pepa.jpg", precio: "38.00", stock: 7 },
  { id: 9, codigo: "KEKE_INGLES", nombre: "Keke Inglés", categoria: "kekes", descripcion: "Frutas confitadas y pasas maceradas en una masa húmeda y aromática.", presentacion: "650 g · Molde rectangular", imagen: "/tienda/productos/keke-ingles.jpg", precio: "26.00", stock: 8 },
  { id: 10, codigo: "KEKE_NARANJA", nombre: "Keke de Naranja Glaseado", categoria: "kekes", descripcion: "Zumo de naranja recién exprimido con glaseado cítrico.", presentacion: "550 g · Corona", imagen: "/tienda/productos/keke-naranja.jpg", precio: "22.00", stock: 12 },
  { id: 11, codigo: "KEKE_PLATANO", nombre: "Keke de Plátano y Cacao", categoria: "kekes", descripcion: "Plátanos maduros, nueces y chispas de chocolate.", presentacion: "Por porción", imagen: "/tienda/productos/keke-platano.jpg", precio: "6.50", stock: 14 },
  { id: 12, codigo: "PANETON", nombre: "Panetón con Higos y Cacao", categoria: "kekes", descripcion: "Masa madre de fermentación lenta con higos y chispas de chocolate.", presentacion: "850 g · Lata", imagen: "/tienda/productos/paneton.jpg", precio: "48.00", stock: 4 },
  { id: 13, codigo: "PIE_LIMON", nombre: "Pie de Limón Individual", categoria: "postres-personales", descripcion: "Masa quebrada de mantequilla, crema de limón y merengue tostado.", presentacion: "120 g · Individual", imagen: "/tienda/productos/pie-limon.jpg", precio: "11.50", stock: 2 },
  { id: 14, codigo: "TARTALETA_LIMON", nombre: "Tartaleta de Limón y Merengue", categoria: "postres-personales", descripcion: "Base crocante de galleta y crema de limón con merengue suizo.", presentacion: "110 g · Individual", imagen: "/tienda/productos/tartaleta-limon.jpg", precio: "9.00", stock: 10 },
  { id: 15, codigo: "ECLAIR", nombre: "Éclair de Vainilla", categoria: "postres-personales", descripcion: "Pasta choux rellena de crema pastelera de vainilla y glaseado de chocolate.", presentacion: "Por unidad", imagen: "/tienda/productos/eclair.jpg", precio: "11.50", stock: 0 },
  { id: 16, codigo: "ROLLO_CANELA", nombre: "Rollo de Canela Glaseado", categoria: "postres-personales", descripcion: "Masa brioche con canela y glaseado de queso crema.", presentacion: "Por unidad", imagen: "/tienda/productos/rollo-canela.jpg", precio: "8.00", stock: 15 },
  { id: 17, codigo: "CHEESECAKE", nombre: "Cheesecake Horneado", categoria: "postres-enteros", descripcion: "Horneado a baño maría, textura densa y cremosa sobre base de galleta.", presentacion: "1.2 kg · 10-12 porciones", imagen: "/tienda/productos/cheesecake.jpg", precio: "68.00", stock: 5 },
  { id: 18, codigo: "TARTALETA_FRESAS", nombre: "Tartaleta de Fresas", categoria: "postres-enteros", descripcion: "Fondo de masa sablé con crema diplomática y fresas frescas.", presentacion: "22 cm · 8 porciones", imagen: "/tienda/productos/tartaleta-fresas.jpg", precio: "45.00", stock: 0 },
  { id: 19, codigo: "TURRON_CAJA", nombre: "Turrón de la Casa", categoria: "postres-enteros", descripcion: "Turrón tradicional en caja para regalar.", presentacion: "Caja 350 g", imagen: "/tienda/productos/turron-caja.jpg", precio: "18.00", stock: 11 },
  { id: 20, codigo: "EMPANADA_CARNE", nombre: "Empanada de Carne", categoria: "bocados", descripcion: "Masa hojaldrada rellena de carne picada a cuchillo, aceituna y huevo.", presentacion: "180 g · Por unidad", imagen: "/tienda/productos/empanada.jpg", precio: "8.50", stock: 20 },
  { id: 21, codigo: "QUICHE_LORRAINE", nombre: "Quiche Lorraine", categoria: "bocados", descripcion: "Masa brisée con tocino ahumado y relleno de huevo y queso.", presentacion: "210 g · Porción", imagen: "/tienda/productos/quiche.jpg", precio: "13.50", stock: 4 },
];

/** Promociones ya aprobadas por un administrador (T05). Aplican a las unidades de un lote. */
export const PROMOCIONES = [
  { id: 101, producto_id: 7, descuento_pct: 20, unidades_lote: 4, vigente_hasta: "20:00" },
  { id: 102, producto_id: 1, descuento_pct: 30, unidades_lote: 6, vigente_hasta: "20:00" },
];
