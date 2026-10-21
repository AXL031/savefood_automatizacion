import Link from "next/link";
import { DATOS_COMERCIO } from "../servicios";
import { MarcaTienda } from "./Encabezado";
import { IconoArchivo } from "./Iconos";

export function Pie() {
  return (
    <footer className="t-pie">
      <div className="t-pie-interior">
        <div className="t-pie-columnas">
          <div className="t-pie-columna">
            <MarcaTienda pequena />
            <p>Panadería y pastelería artesanal horneada cada día en {DATOS_COMERCIO.ciudad.split(",")[0]}.</p>
            <div className="t-pie-sello">
              <IconoArchivo nombre="garantia" />
              <div><strong>Stock en tiempo real</strong><span>Lo que ves disponible está en vitrina.</span></div>
            </div>
          </div>
          <div className="t-pie-columna">
            <h2>Horarios de atención</h2>
            <ul className="t-pie-horarios">
              {DATOS_COMERCIO.horarios.map((h) => <li key={h.dias}><strong>{h.dias}</strong><span>{h.horas}</span></li>)}
            </ul>
          </div>
          <div className="t-pie-columna">
            <h2>Nuestra sucursal</h2>
            <p><strong>{DATOS_COMERCIO.nombre}</strong><br />{DATOS_COMERCIO.ciudad}</p>
            <p className="t-pie-nota"><IconoArchivo nombre="horno" /> Entregas a domicilio en Lima Metropolitana</p>
          </div>
          <div className="t-pie-columna">
            <h2>Tu cuenta</h2>
            <p>Navega libremente. Solo te pediremos iniciar sesión con Google al confirmar tu pedido.</p>
            <Link href="/tienda/pedidos" className="t-pie-enlace">Ver mis pedidos <IconoArchivo nombre="flecha" /></Link>
          </div>
        </div>
        <div className="t-pie-legal">
          <span><IconoArchivo nombre="copyright" /> {new Date().getFullYear()} {DATOS_COMERCIO.nombre}. Pagos simulados con fines académicos.</span>
        </div>
      </div>
    </footer>
  );
}
