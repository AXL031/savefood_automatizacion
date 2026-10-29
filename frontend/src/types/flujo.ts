export type ConfiguracionFlujo = {
  prueba_repetible?: boolean;
  producto_ids: number[]; modelo_id: number | null; fecha_objetivo_demo: string;
  hora_simulada: string; primera_ejecucion_local: string; dias: number;
  modo_envio_pedidos: "REQUIERE_APROBACION" | "AUTOMATICO";
};
export type Requisito = { titulo: string; listo: boolean; motivo: string; enlace: string };
export type AvisoCompra = { codigo: string; titulo: string; motivo: string; recomendacion: string; enlace: string; ingrediente_id?: number; proveedor_id?: number };
export type DiagnosticoFlujo = { listo: boolean; requisitos: Requisito[]; avisos: AvisoCompra[]; compras_listas: boolean; modelo_id: number | null; productos: string[] };
