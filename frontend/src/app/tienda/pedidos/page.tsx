"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useTienda } from "@/tienda/contexto";
import { soles } from "@/tienda/dinero";
import { listarPedidos } from "@/tienda/servicios";
import type { PedidoCliente } from "@/tienda/tipos";
import { DetallePedido, fechaPedido } from "@/tienda/componentes/DetallePedido";
import { EstadoCarga } from "@/tienda/componentes/EstadoCarga";

export default function PaginaPedidos() {
  const { sesion, abrirLogin } = useTienda();
  const [pedidos, setPedidos] = useState<PedidoCliente[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sesion) return;
    const control = new AbortController();
    listarPedidos(sesion, control.signal).then(setPedidos).catch((e: unknown) => {
      if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudieron cargar tus pedidos.");
    });
    return () => control.abort();
  }, [sesion]);

  if (!sesion) {
    return (
      <div className="t-contenedor t-estado">
        <h1>Mis pedidos</h1>
        <p>Inicia sesión con Google para ver los pedidos que confirmaste.</p>
        <button type="button" className="t-boton-primario" onClick={abrirLogin}>Iniciar sesión</button>
      </div>
    );
  }
  if (error) return <EstadoCarga error={error} />;
  if (!pedidos) return <EstadoCarga />;

  return (
    <div className="t-contenedor t-pedidos">
      <header className="t-menu-titulo">
        <h1>Mis pedidos</h1>
        <p>Pedidos confirmados con {sesion.cliente.correo}.</p>
      </header>
      {!pedidos.length ? (
        <div className="t-vacio"><h2>Aún no tienes pedidos</h2><p>Cuando confirmes una compra aparecerá aquí.</p><Link href="/tienda/menu" className="t-boton-primario">Ver el menú</Link></div>
      ) : (
        <div className="t-pedidos-lista">
          {pedidos.map((p) => (
            <details key={p.id} className="t-pedido">
              <summary>
                <span><strong>Pedido #{p.id}</strong><small>{fechaPedido(p.creado_en)}</small></span>
                <span className="t-chip-ok t-chip-pequeno">Confirmado</span>
                <strong>{soles(p.total)}</strong>
              </summary>
              <DetallePedido pedido={p} />
            </details>
          ))}
        </div>
      )}
    </div>
  );
}
