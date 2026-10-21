"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useTienda } from "../contexto";
import { DATOS_COMERCIO } from "../servicios";
import { Icono, IconoArchivo } from "./Iconos";
import { LogoTienda } from "./LogoTienda";

const ENLACES = [
  { href: "/tienda", texto: "Inicio" },
  { href: "/tienda/menu", texto: "Menú de Especialidades" },
  { href: "/tienda/menu#categorias", texto: "Categorías" },
];

export function MarcaTienda({ pequena = false }: { pequena?: boolean }) {
  return (
    <span className={`t-marca${pequena ? " t-marca-pequena" : ""}`}>
      <LogoTienda tamano={pequena ? 40 : 54} />
      <span className="t-marca-textos">
        <span className="t-marca-nombre">{DATOS_COMERCIO.nombre}</span>
        {pequena ? null : <span className="t-marca-lema">{DATOS_COMERCIO.lema}</span>}
      </span>
    </span>
  );
}

export function Encabezado() {
  const ruta = usePathname();
  const router = useRouter();
  const { unidadesCarrito, sesion, guardarSesion, abrirLogin } = useTienda();
  const [busqueda, setBusqueda] = useState("");
  const [menuCuenta, setMenuCuenta] = useState(false);
  const cuenta = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuCuenta) return;
    const cerrar = (e: MouseEvent) => { if (!cuenta.current?.contains(e.target as Node)) setMenuCuenta(false); };
    const escape = (e: KeyboardEvent) => { if (e.key === "Escape") setMenuCuenta(false); };
    document.addEventListener("mousedown", cerrar);
    document.addEventListener("keydown", escape);
    return () => { document.removeEventListener("mousedown", cerrar); document.removeEventListener("keydown", escape); };
  }, [menuCuenta]);

  return (
    <header className="t-encabezado">
      <div className="t-encabezado-interior">
        <Link href="/tienda" className="t-encabezado-marca" aria-label={`${DATOS_COMERCIO.nombre}, inicio`}><MarcaTienda /></Link>
        <nav className="t-nav" aria-label="Tienda">
          {ENLACES.map((e) => {
            const activo = e.href === ruta || (e.href === "/tienda/menu" && ruta === "/tienda/menu");
            return <Link key={e.texto} href={e.href} className={activo && !e.href.includes("#") ? "t-nav-activo" : ""} aria-current={activo && !e.href.includes("#") ? "page" : undefined}>{e.texto}</Link>;
          })}
        </nav>
        <div className="t-encabezado-acciones">
          <form className="t-buscador" role="search" onSubmit={(e) => { e.preventDefault(); router.push(`/tienda/menu?buscar=${encodeURIComponent(busqueda.trim())}`); }}>
            <IconoArchivo nombre="buscar" />
            <input type="search" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} placeholder="Buscar croissants, tortas…" aria-label="Buscar productos" />
          </form>
          <Link href="/tienda/carrito" className="t-boton-canasta" aria-label={`Canasta, ${unidadesCarrito} productos`}>
            <IconoArchivo nombre="canasta" />
            {unidadesCarrito > 0 ? <span className="t-canasta-contador">{unidadesCarrito > 99 ? "99+" : unidadesCarrito}</span> : null}
          </Link>
          <div className="t-cuenta" ref={cuenta}>
            <button type="button" className="t-boton-cuenta" aria-haspopup="menu" aria-expanded={menuCuenta}
              aria-label={sesion ? `Cuenta de ${sesion.cliente.nombre}` : "Iniciar sesión"}
              onClick={() => (sesion ? setMenuCuenta(!menuCuenta) : abrirLogin())}>
              {sesion ? <span className="t-inicial">{sesion.cliente.nombre.charAt(0).toUpperCase()}</span> : <IconoArchivo nombre="usuario" />}
            </button>
            {menuCuenta && sesion ? (
              <div className="t-menu-cuenta" role="menu">
                <p><strong>{sesion.cliente.nombre}</strong><span>{sesion.cliente.correo}</span></p>
                <Link role="menuitem" href="/tienda/pedidos" onClick={() => setMenuCuenta(false)}><Icono nombre="bolsa" />Mis pedidos</Link>
                <button role="menuitem" type="button" onClick={() => { guardarSesion(null); setMenuCuenta(false); }}><Icono nombre="salir" />Cerrar sesión</button>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </header>
  );
}
