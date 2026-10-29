"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { useTienda } from "@/tienda/contexto";
import type { EstadoStock } from "@/tienda/tipos";
import { EstadoCarga } from "@/tienda/componentes/EstadoCarga";
import { Icono, IconoArchivo } from "@/tienda/componentes/Iconos";
import { TarjetaProducto } from "@/tienda/componentes/TarjetaProducto";
import { LogoTienda } from "@/tienda/componentes/LogoTienda";

type Filtro = "TODOS" | EstadoStock;
const FILTROS: { valor: Filtro; texto: string }[] = [
  { valor: "TODOS", texto: "Todos los productos" },
  { valor: "DISPONIBLE", texto: "Solo disponibles" },
  { valor: "ULTIMAS_UNIDADES", texto: "Últimas unidades" },
  { valor: "AGOTADO", texto: "Agotados" },
];

const normalizar = (t: string) => t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

function Menu() {
  const { catalogo, errorCatalogo, recargarCatalogo } = useTienda();
  const parametros = useSearchParams();
  const [busqueda, setBusqueda] = useState("");
  const [filtro, setFiltro] = useState<Filtro>("TODOS");

  useEffect(() => { setBusqueda(parametros.get("buscar") ?? ""); }, [parametros]);

  const visibles = useMemo(() => {
    if (!catalogo) return [];
    const texto = normalizar(busqueda.trim());
    return catalogo.productos.filter((p) =>
      (filtro === "TODOS" || p.estado_stock === filtro) &&
      (!texto || normalizar(`${p.nombre} ${p.descripcion}`).includes(texto)));
  }, [catalogo, busqueda, filtro]);

  if (!catalogo) return <EstadoCarga error={errorCatalogo} alReintentar={recargarCatalogo} />;
  if (!catalogo.productos.length) return <div className="t-contenedor t-estado"><h1>Estamos preparando el menú</h1><p>La pastelería todavía no ha publicado productos.</p><button className="t-boton-contorno" onClick={recargarCatalogo}>Actualizar menú</button></div>;

  const conteo = (f: Filtro) => catalogo.productos.filter((p) => f === "TODOS" || p.estado_stock === f).length;
  const promociones = visibles.filter((p) => p.promocion);
  const nombreCategoria = (codigo: string) => catalogo.categorias.find((c) => c.codigo === codigo)?.nombre;

  return (
    <div className="t-contenedor t-menu">
      <header className="t-menu-titulo">
        <h1>Catálogo de especialidades</h1>
        <p>Recetas de la casa preparadas cada día. El estado de cada producto se actualiza automáticamente con nuestra vitrina.</p>
      </header>

      <div className="t-menu-grid">
        <aside className="t-menu-lateral" aria-label="Filtros del catálogo">
          <div className="t-panel">
            <label className="t-panel-titulo" htmlFor="t-busqueda-menu"><IconoArchivo nombre="buscar" />Búsqueda</label>
            <input id="t-busqueda-menu" type="search" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} placeholder="Buscar brioche, selva negra…" className="t-campo-redondo" />
          </div>
          <fieldset className="t-panel">
            <legend className="t-panel-titulo t-panel-titulo-fila"><span>Estado en mostrador</span><span className="t-panel-hoy">Hoy</span></legend>
            {FILTROS.map((f) => (
              <label key={f.valor} className={`t-filtro${filtro === f.valor ? " t-filtro-activo" : ""}`}>
                <input type="radio" name="estado" value={f.valor} checked={filtro === f.valor} onChange={() => setFiltro(f.valor)} />
                <span className={`t-filtro-punto t-filtro-${f.valor.toLowerCase()}`} aria-hidden="true" />
                <span className="t-filtro-texto">{f.texto}</span>
                <span className="t-filtro-conteo">{conteo(f.valor)}</span>
              </label>
            ))}
          </fieldset>
          <nav className="t-panel" id="categorias" aria-label="Secciones del menú">
            <span className="t-panel-titulo">Secciones del menú</span>
            {promociones.length ? <a href="#promociones" className="t-seccion-enlace t-seccion-enlace-activa"><Icono nombre="estrella" tamano={13} />Promociones del día<span aria-hidden="true">›</span></a> : null}
            {catalogo.categorias.map((c) => <a key={c.codigo} href={`#${c.codigo}`} className="t-seccion-enlace">{c.nombre}<span aria-hidden="true">›</span></a>)}
          </nav>
          <div className="t-consejo">
            <LogoTienda tamano={48} />
            <span className="t-antetitulo t-antetitulo-acento">Consejo de la casa</span>
            <strong>Pide temprano</strong>
            <p>Los productos con “Últimas unidades” suelen agotarse antes del mediodía. Agrégalos a tu canasta y confirma tu pedido.</p>
          </div>
        </aside>

        <div className="t-menu-contenido">
          {!visibles.length ? (
            <div className="t-vacio"><h2>No encontramos productos</h2><p>Prueba con otra búsqueda o cambia el filtro de estado.</p></div>
          ) : null}

          {promociones.length ? (
            <section id="promociones" className="t-menu-seccion">
              <div className="t-menu-seccion-cabecera">
                <h2><span className="t-menu-seccion-icono"><Icono nombre="estrella" tamano={16} /></span>Promociones del día</h2>
              </div>
              <p className="t-menu-seccion-texto">Descuentos sobre lotes que conviene vender hoy, válidos hasta agotar o hasta el cierre.</p>
              <div className="t-rejilla-3">{promociones.map((p) => <TarjetaProducto key={p.id} producto={p} categoria={nombreCategoria(p.categoria)} />)}</div>
            </section>
          ) : null}

          {catalogo.categorias.map((c) => {
            const productos = visibles.filter((p) => p.categoria === c.codigo);
            if (!productos.length) return null;
            return (
              <section key={c.codigo} id={c.codigo} className="t-menu-seccion">
                <div className="t-menu-seccion-cabecera">
                  <h2>{c.nombre}</h2>
                  <span className="t-menu-seccion-conteo">{productos.length} {productos.length === 1 ? "variedad" : "variedades"}</span>
                </div>
                <p className="t-menu-seccion-texto">{c.descripcion}</p>
                <div className="t-rejilla-3">{productos.map((p) => <TarjetaProducto key={p.id} producto={p} />)}</div>
              </section>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default function PaginaMenu() {
  return <Suspense fallback={<EstadoCarga />}><Menu /></Suspense>;
}
