export type ConfiguracionFlujo = {
  producto_ids: number[]; modelo_id: number | null; fecha_objetivo_demo: string;
  hora_simulada: string; primera_ejecucion_local: string; dias: number;
  modo_envio_pedidos: "REQUIERE_APROBACION" | "AUTOMATICO";
};
export type Requisito = { titulo: string; listo: boolean; motivo: string; enlace: string };
export type DiagnosticoFlujo = { listo: boolean; requisitos: Requisito[]; modelo_id: number | null; productos: string[] };
