"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useTienda } from "@/tienda/contexto";
import { obtenerPedido } from "@/tienda/servicios";
import type { PedidoCliente } from "@/tienda/tipos";
import { DetallePedido } from "@/tienda/componentes/DetallePedido";
import { EstadoCarga } from "@/tienda/componentes/EstadoCarga";
import { Icono } from "@/tienda/componentes/Iconos";

import { DetallePagoPayme } from "@/tienda/componentes/DetallePagoPayme";

export default function PaginaPedido() {
  const { id } = useParams<{ id: string }>();
  const { sesion, abrirLogin } = useTienda();
  const [pedido, setPedido] = useState<PedidoCliente | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (id.startsWith("payme-") || !sesion) return;
    const control = new AbortController();
    obtenerPedido(Number(id), sesion, control.signal).then(setPedido).catch((e: unknown) => {
      if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo cargar el pedido.");
    });
    return () => control.abort();
  }, [id, sesion]);

  if (id.startsWith("payme-")) return <DetallePagoPayme id={id.slice(6)} />;

  if (!sesion) {
    return (
      <div className="t-contenedor t-estado">
        <h1>Inicia sesión para ver tu pedido</h1>
        <button type="button" className="t-boton-primario" onClick={abrirLogin}>Iniciar sesión</button>
      </div>
    );
  }
  if (error) return <EstadoCarga error={error} />;
  if (!pedido) return <EstadoCarga />;

  return (
    <div className="t-contenedor t-confirmacion">
      <div className="t-confirmacion-tarjeta">
        <span className="t-confirmacion-icono"><Icono nombre="check" tamano={30} /></span>
        <span className="t-antetitulo t-antetitulo-acento">Pedido #{pedido.id} confirmado</span>
        <h1>¡Gracias, {sesion.cliente.nombre.split(" ")[0]}!</h1>
        <p>Registramos tu pedido y tu pago. Te contactaremos al celular indicado para coordinar la entrega.</p>
        <DetallePedido pedido={pedido} />
        <div className="t-confirmacion-acciones">
          <Link href="/tienda/menu" className="t-boton-primario">Seguir comprando</Link>
          <Link href="/tienda/pedidos" className="t-boton-contorno">Ver mis pedidos</Link>
        </div>
      </div>
    </div>
  );
}
