"use client";

import Link from "next/link";
import { useTienda } from "@/tienda/contexto";
import { soles } from "@/tienda/dinero";
import { Icono, IconoArchivo } from "@/tienda/componentes/Iconos";
import { TarjetaProducto, TarjetaProductoHorizontal } from "@/tienda/componentes/TarjetaProducto";
import { EstadoCarga } from "@/tienda/componentes/EstadoCarga";
import { LogoTienda } from "@/tienda/componentes/LogoTienda";

export default function InicioTienda() {
  const { catalogo, errorCatalogo, recargarCatalogo, agregar } = useTienda();
  if (!catalogo) return <EstadoCarga error={errorCatalogo} alReintentar={recargarCatalogo} />;

  const nombreCategoria = (codigo: string) => catalogo.categorias.find((c) => c.codigo === codigo)?.nombre;
  const conPromo = catalogo.productos.filter((p) => p.promocion && p.estado_stock !== "AGOTADO");
  const destacada = conPromo[0];
  // Destacados: promociones aprobadas primero, luego disponibles del día, y un agotado para mostrar el estado.
  const destacados = [
    ...conPromo,
    ...catalogo.productos.filter((p) => !p.promocion && p.estado_stock === "DISPONIBLE"),
  ].slice(0, 3);
  const agotado = catalogo.productos.find((p) => p.estado_stock === "AGOTADO");
  const vitrina = agotado ? [...destacados, agotado] : catalogo.productos.slice(0, 4);
  const favoritos = catalogo.productos.filter((p) => !vitrina.includes(p) && p.estado_stock !== "AGOTADO").slice(0, 4);

  return (
    <>
      <section className="t-hero">
        <div className="t-contenedor t-hero-grid">
          <div className="t-hero-texto">
            <h1>Horneado a diario<br />con amor y masa madre.</h1>
            <p>Desde temprano preparamos panes, tortas y postres con insumos frescos. Elige lo que quieres, revisa qué hay en vitrina en tiempo real y recíbelo en tu casa.</p>
            {destacada?.promocion ? (
              <div className="t-hero-oferta">
                <span className="t-hero-oferta-icono"><Icono nombre="estrella" tamano={20} /></span>
                <div className="t-hero-oferta-texto">
                  <span className="t-chip-oferta">Promoción del día</span>
                  <strong>{destacada.nombre} con {destacada.promocion.descuento_pct}% de descuento</strong>
                  <span>Válido hasta agotar el lote o hasta las {destacada.promocion.vigente_hasta}.</span>
                </div>
                <div className="t-hero-oferta-precio">
                  <span className="t-precio-antes">{soles(destacada.promocion.precio_normal)}</span>
                  <strong>{soles(destacada.promocion.precio_promocional)}</strong>
                </div>
                <button type="button" className="t-boton-primario" onClick={() => agregar(destacada.id)}>Aprovechar oferta <Icono nombre="adelante" tamano={14} /></button>
              </div>
            ) : null}
            <ul className="t-hero-ventajas">
              <li><Icono nombre="check" tamano={14} />Horneado del día</li>
              <li><Icono nombre="reloj" tamano={14} />Stock actualizado en vivo</li>
              <li><Icono nombre="camion" tamano={14} />Entrega a domicilio en Lima</li>
            </ul>
          </div>
          <figure className="t-hero-imagen">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/tienda/hero-horno.jpg" alt="Bandeja de croissants recién salidos del horno" />
            <figcaption>
              <LogoTienda tamano={46} />
              <span><strong>Hecho en casa</strong>“El sabor de siempre, horneado cada mañana.”</span>
            </figcaption>
          </figure>
        </div>
      </section>

      <section className="t-seccion t-seccion-crema" id="especialidades">
        <div className="t-contenedor">
          <div className="t-seccion-cabecera">
            <div><span className="t-antetitulo">La despensa del día</span><h2>Explora por especialidad</h2></div>
            <Link href="/tienda/menu" className="t-enlace-suave">Ver el menú completo <IconoArchivo nombre="flecha" /></Link>
          </div>
          <div className="t-categorias">
            {catalogo.categorias.map((c) => (
              <Link key={c.codigo} href={`/tienda/menu#${c.codigo}`} className="t-categoria">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={c.imagen} alt="" />
                <strong>{c.nombre}</strong>
                <span>{c.descripcion}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="t-seccion">
        <div className="t-contenedor">
          <div className="t-seccion-cabecera">
            <div>
              <span className="t-antetitulo t-antetitulo-acento"><Icono nombre="estrella" tamano={12} />Selección del día</span>
              <h2>Lo más destacado y promociones</h2>
              <p>Las promociones aparecen cuando el sistema detecta stock que conviene vender hoy y la pastelería las aprueba.</p>
            </div>
            <Link href="/tienda/menu" className="t-boton-contorno">Ver catálogo completo <IconoArchivo nombre="flecha" /></Link>
          </div>
          <div className="t-rejilla-4">
            {vitrina.map((p) => <TarjetaProducto key={p.id} producto={p} categoria={nombreCategoria(p.categoria)} />)}
          </div>
        </div>
      </section>

      <section className="t-contenedor">
        <div className="t-banner">
          <span className="t-banner-icono"><IconoArchivo nombre="canasta" escala={1.4} /></span>
          <div>
            <span className="t-banner-antetitulo">Compra sin complicaciones</span>
            <h2>Explora libremente sin registrarte.</h2>
            <p>Llena tu canasta a tu ritmo. Solo al confirmar te pediremos iniciar sesión con Google, la dirección de entrega y el pago.</p>
          </div>
          <Link href="/tienda/menu" className="t-boton-claro">Armar mi pedido</Link>
        </div>
      </section>

      {favoritos.length ? (
        <section className="t-seccion">
          <div className="t-contenedor">
            <div className="t-seccion-cabecera">
              <div><span className="t-antetitulo">Tradición de la casa</span><h2>Favoritos frecuentes</h2><p>Los que nunca faltan en el desayuno o el lonche.</p></div>
            </div>
            <div className="t-rejilla-2">
              {favoritos.map((p) => <TarjetaProductoHorizontal key={p.id} producto={p} categoria={nombreCategoria(p.categoria)} />)}
            </div>
          </div>
        </section>
      ) : null}

      <section className="t-seccion t-seccion-crema">
        <div className="t-contenedor">
          <div className="t-seccion-cabecera t-centrado">
            <div><span className="t-antetitulo">Cómo funciona</span><h2>Del horno a tu mesa</h2><p>Nuestra vitrina y nuestras promociones se actualizan solas con el inventario de la pastelería.</p></div>
          </div>
          <div className="t-rejilla-3">
            <article className="t-valor">
              <span className="t-valor-icono"><LogoTienda tamano={60} /></span>
              <h3>Horneado del día</h3>
              <p>Cada producto se elabora con nuestras recetas y se ofrece mientras haya unidades en vitrina.</p>
            </article>
            <article className="t-valor">
              <span className="t-valor-icono t-valor-icono-salmon"><Icono nombre="reloj" tamano={22} /></span>
              <h3>Stock en tiempo real</h3>
              <p>Verás si un producto está disponible, en últimas unidades o agotado. Al comprar, la vitrina se actualiza.</p>
            </article>
            <article className="t-valor">
              <span className="t-valor-icono t-valor-icono-crema"><Icono nombre="estrella" tamano={22} /></span>
              <h3>Promociones del momento</h3>
              <p>Cuando un lote necesita salir hoy, la pastelería aprueba un descuento y lo verás aquí.</p>
            </article>
          </div>
        </div>
      </section>
    </>
  );
}
