import { soles } from "../dinero";
import type { MetodoPagoSimulado, PedidoCliente } from "../tipos";

export const TEXTO_METODO: Record<MetodoPagoSimulado, string> = {
  TARJETA_SIMULADA: "Tarjeta",
  YAPE_SIMULADO: "Yape",
  PLIN_SIMULADO: "Plin",
};

export function fechaPedido(iso: string) {
  return new Intl.DateTimeFormat("es-PE", { dateStyle: "medium", timeStyle: "short", timeZone: "America/Lima" }).format(new Date(iso));
}

export function DetallePedido({ pedido }: { pedido: PedidoCliente }) {
  return (
    <div className="t-detalle-pedido">
      <ul className="t-detalle-lineas">
        {pedido.lineas.map((l) => (
          <li key={l.producto_id}><span>{l.cantidad} × {l.nombre}</span><strong>{soles(l.subtotal)}</strong></li>
        ))}
        <li className="t-detalle-total"><span>Total simulado</span><strong>{soles(pedido.total)}</strong></li>
      </ul>
      <dl className="t-detalle-datos">
        <div><dt>Entrega en</dt><dd>{pedido.entrega.direccion}, {pedido.entrega.distrito}{pedido.entrega.referencia ? ` (${pedido.entrega.referencia})` : ""}</dd></div>
        <div><dt>Recibe</dt><dd>{pedido.entrega.nombre_receptor} · +51 {pedido.entrega.celular}</dd></div>
        <div><dt>Pago simulado</dt><dd>{TEXTO_METODO[pedido.pago.metodo]} · Sin cargo real · Ref. {pedido.pago.referencia}</dd></div>
        <div><dt>Fecha</dt><dd>{fechaPedido(pedido.creado_en)}</dd></div>
      </dl>
    </div>
  );
}
