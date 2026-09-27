export type Notificacion = {
  id: number;
  tipo: string;
  titulo: string;
  mensaje: string;
  estado: "PENDIENTE" | "ENVIADA" | "FALLIDA";
  creado_en: string;
  enviado_en: string | null;
  ejecucion_id?: number | null;
};
