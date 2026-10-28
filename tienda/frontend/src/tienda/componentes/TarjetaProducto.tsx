"use client";

import { useTienda } from "../contexto";
import { soles } from "../dinero";
import type { ProductoTienda } from "../tipos";
import { EstadoStock } from "./EstadoStock";
import { Icono } from "./Iconos";

function Precio({ producto }: { producto: ProductoTienda }) {
  if (producto.promocion) {
    return (
      <div className="t-precio">
        <span className="t-precio-antes">{soles(producto.promocion.precio_normal)}</span>
        <strong className="t-precio-promo">{soles(producto.promocion.precio_promocional)}</strong>
      </div>
    );
  }
  return <div className="t-precio"><strong>{soles(producto.precio)}</strong></div>;
}

function BotonAgregar({ producto, compacto = false }: { producto: ProductoTienda; compacto?: boolean }) {
  const { agregar } = useTienda();
  const agotado = producto.estado_stock === "AGOTADO";
  return (
    <button type="button" className={compacto ? "t-boton-agregar-redondo" : "t-boton-agregar"} disabled={agotado}
      onClick={() => agregar(producto.id)} aria-label={agotado ? `${producto.nombre} agotado` : `Agregar ${producto.nombre} a la canasta`}>
      {agotado ? "Agotado" : <><Icono nombre="mas" tamano={compacto ? 14 : 12} />{compacto ? null : "Agregar"}</>}
    </button>
  );
}

/** Tarjeta vertical de catálogo (destacados y menú). */
export function TarjetaProducto({ producto, categoria }: { producto: ProductoTienda; categoria?: string }) {
  const agotado = producto.estado_stock === "AGOTADO";
  return (
    <article className={`t-tarjeta${agotado ? " t-tarjeta-agotada" : ""}`}>
      <div className="t-tarjeta-imagen">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        {producto.imagen ? <img src={producto.imagen} alt={producto.nombre} loading="lazy" /> : <div className="t-imagen-pendiente" aria-label="Imagen pendiente">Imagen pendiente</div>}
        <div className="t-tarjeta-chips">
          <EstadoStock estado={producto.estado_stock} />
          {producto.promocion ? <span className="t-chip-promo">-{producto.promocion.descuento_pct}% Descuento</span> : null}
        </div>
        {!agotado ? <div className="t-tarjeta-flotante"><BotonAgregar producto={producto} compacto /></div> : null}
      </div>
      <div className="t-tarjeta-cuerpo">
        {categoria ? <span className="t-tarjeta-categoria">{categoria}</span> : null}
        <h3>{producto.nombre}</h3>
        <p className="t-tarjeta-descripcion">{producto.descripcion}</p>
        <div className="t-tarjeta-pie">
          <div>
            <span className="t-tarjeta-presentacion">{producto.presentacion}</span>
            <Precio producto={producto} />
          </div>
          <BotonAgregar producto={producto} />
        </div>
      </div>
    </article>
  );
}

/** Tarjeta horizontal de la sección Favoritos. */
export function TarjetaProductoHorizontal({ producto, categoria }: { producto: ProductoTienda; categoria?: string }) {
  return (
    <article className={`t-tarjeta-h${producto.estado_stock === "AGOTADO" ? " t-tarjeta-agotada" : ""}`}>
      <div className="t-tarjeta-h-imagen">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        {producto.imagen ? <img src={producto.imagen} alt={producto.nombre} loading="lazy" /> : <div className="t-imagen-pendiente" aria-label="Imagen pendiente">Imagen pendiente</div>}
      </div>
      <div className="t-tarjeta-h-cuerpo">
        <div className="t-tarjeta-h-cabecera">
          {categoria ? <span className="t-tarjeta-categoria">{categoria}</span> : <span />}
          <EstadoStock estado={producto.estado_stock} />
        </div>
        <h3>{producto.nombre}</h3>
        <p className="t-tarjeta-descripcion">{producto.descripcion}</p>
        <div className="t-tarjeta-pie">
          <div className="t-precio-linea"><Precio producto={producto} /><span className="t-tarjeta-presentacion">/ {producto.presentacion}</span></div>
          <BotonAgregar producto={producto} />
        </div>
      </div>
    </article>
  );
}
