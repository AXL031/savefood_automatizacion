"use client";
import Link from "next/link";
import { PagosPaymeGuardados } from "@/tienda/componentes/DetallePagoPayme";

export default function PaginaPedidos() {
  return <div className="t-contenedor t-pedidos">
    <header className="t-menu-titulo"><h1>Mis compras y pagos</h1><p>Consulta tus operaciones desde el navegador donde las iniciaste. Puedes comprar como invitado.</p></header>
    <PagosPaymeGuardados />
    <p>Un pago pendiente o un código generado todavía no confirma una compra. Revisa su estado antes de volver a pagar.</p>
    <Link href="/tienda/menu" className="t-boton-contorno">Volver al menú</Link>
  </div>;
}
