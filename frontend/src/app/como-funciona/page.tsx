"use client";
import Link from "next/link";
import { useEffect, useRef, type CSSProperties } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { ETAPAS, ETAPAS_CICLO, Icono, visibles, type NombreIcono } from "@/components/layout/navegacion";

type Destino = { href: string; texto: string };
type Quien = "auto" | "tu" | "ambos";
type Paso = { etapa: string; icono: NombreIcono; titulo: string; texto: string; ejemplo: string; quien: Quien; destinos: Destino[] };

// Nombres de pantalla tomados del mapa de navegación para que los enlaces no se desactualicen.
const pantalla = (href: string): Destino => {
  const encontrada = ETAPAS.flatMap((e) => e.pantallas).find((p) => p.href === href);
  return { href, texto: encontrada?.texto ?? href };
};

const PASOS: Paso[] = [
  { etapa: "preparar", icono: "datos", titulo: "Cargas tus datos", quien: "tu",
    texto: "Subes el historial de ventas, el catálogo de productos y el stock inicial. Es la base de todo: sin historia no hay pronóstico.",
    ejemplo: "Seis meses de ventas de la panadería en un archivo.", destinos: [pantalla("/inicializacion"), pantalla("/productos")] },
  { etapa: "preparar", icono: "receta", titulo: "Defines ingredientes y recetas", quien: "tu",
    texto: "Cada producto tiene una receta: cuánto usa de cada insumo por unidad. Así FoodSave sabe qué hay que comprar.",
    ejemplo: "1 croissant = 50 g de harina + 20 g de mantequilla.", destinos: [pantalla("/ingredientes"), pantalla("/recetas")] },
  { etapa: "pronosticar", icono: "pronostico", titulo: "El modelo aprende de tus ventas", quien: "auto",
    texto: "Un modelo de inteligencia artificial estudia tus ventas pasadas: días de la semana, temporadas y tendencias. Solo usa historia anterior al día que predice.",
    ejemplo: "Descubre que los sábados se venden más croissants.", destinos: [pantalla("/pronosticos")] },
  { etapa: "planificar", icono: "automatizacion", titulo: "La automatización arranca sola", quien: "auto",
    texto: "A la hora que programaste, FoodSave inicia el ciclo del día siguiente. Cada paso queda registrado con su estado, intentos y errores.",
    ejemplo: "Todos los días a las 18:00, sin que tengas que entrar.", destinos: [pantalla("/automatizaciones")] },
  { etapa: "planificar", icono: "plan", titulo: "Pronostica y propone cuánto producir", quien: "auto",
    texto: "Calcula cuántas unidades se venderán mañana de cada producto y arma el plan de producción.",
    ejemplo: "Mañana se venderán 120 croissants: producir 120.", destinos: [pantalla("/planificacion")] },
  { etapa: "planificar", icono: "ingrediente", titulo: "Detecta los insumos faltantes", quien: "auto",
    texto: "Multiplica el plan por las recetas y lo compara con el stock disponible por lote. Lo que no alcanza es un faltante.",
    ejemplo: "Se necesitan 6 kg de harina, hay 4 kg: faltan 2 kg.", destinos: [pantalla("/planificacion"), pantalla("/inventario")] },
  { etapa: "abastecer", icono: "pedido", titulo: "Arma un pedido por proveedor", quien: "auto",
    texto: "Agrupa los faltantes y elige la oferta preferida de cada proveedor. Ojo: un pedido todavía no cambia tu stock.",
    ejemplo: "Pedido a Molinos del Sur: 2 kg de harina.", destinos: [pantalla("/compras"), pantalla("/proveedores")] },
  { etapa: "abastecer", icono: "check", titulo: "Revisas y apruebas", quien: "tu",
    texto: "Si tu comercio pide aprobación, revisas el texto y el destino antes de enviar. También se puede dejar en envío automático.",
    ejemplo: "Lees el mensaje y pulsas «Aprobar».", destinos: [pantalla("/compras"), pantalla("/configuracion")] },
  { etapa: "abastecer", icono: "proveedor", titulo: "Se envía por Telegram", quien: "auto",
    texto: "El pedido llega al chat del proveedor. Si el envío falla o queda en duda, se marca para verificar: nunca se reenvía a ciegas.",
    ejemplo: "Mensaje entregado al chat de Molinos del Sur.", destinos: [pantalla("/proveedores"), pantalla("/notificaciones")] },
  { etapa: "abastecer", icono: "inventario", titulo: "Recibes la mercadería", quien: "tu",
    texto: "Al registrar la recepción, recién ahí sube el stock y se crea un lote con su fecha de vencimiento.",
    ejemplo: "Entran 2 kg de harina que vencen el 15/12.", destinos: [pantalla("/compras"), pantalla("/inventario")] },
  { etapa: "planificar", icono: "operacion", titulo: "Produces por tandas", quien: "tu",
    texto: "Registras lo que preparas durante el día. El inventario descuenta insumos y suma producto terminado.",
    ejemplo: "Tanda de 60 croissants a las 6:00.", destinos: [pantalla("/operaciones")] },
  { etapa: "vender", icono: "venta", titulo: "Vendes en caja o en la tienda", quien: "tu",
    texto: "Cada venta descuenta stock y se suma al historial que el modelo usará para aprender.",
    ejemplo: "Ticket de 3 croissants en caja.", destinos: [pantalla("/ventas"), pantalla("/tienda-admin")] },
  { etapa: "vender", icono: "promocion", titulo: "Mueves los excedentes", quien: "ambos",
    texto: "Si un lote está por vencer y sobra, FoodSave sugiere un descuento. Solo se publica cuando tú lo apruebas.",
    ejemplo: "20 % de descuento en brioches que vencen mañana.", destinos: [pantalla("/promociones"), pantalla("/tienda-admin")] },
  { etapa: "evaluar", icono: "evaluacion", titulo: "Mides y mejoras", quien: "auto",
    texto: "Compara lo pronosticado con lo vendido de verdad. Un día sin registro de venta no se cuenta como cero.",
    ejemplo: "Esta semana el pronóstico se equivocó un 12 % en promedio.", destinos: [pantalla("/panel"), pantalla("/informes")] },
];

const EJEMPLO = [
  { valor: "120", unidad: "croissants", texto: "pronosticados para mañana", href: "/pronosticos" },
  { valor: "120", unidad: "a producir", texto: "según el plan", href: "/planificacion" },
  { valor: "6 kg", unidad: "de harina", texto: "120 × 50 g de la receta", href: "/recetas" },
  { valor: "4 kg", unidad: "en stock", texto: "suma de lotes vigentes", href: "/inventario" },
  { valor: "2 kg", unidad: "faltantes", texto: "6 kg − 4 kg", href: "/planificacion" },
  { valor: "1", unidad: "pedido", texto: "a Molinos del Sur por Telegram", href: "/compras" },
];

const QUIEN: Record<Quien, { texto: string; icono: NombreIcono }> = {
  auto: { texto: "Automático", icono: "chispa" },
  tu: { texto: "Lo haces tú", icono: "mano" },
  ambos: { texto: "Sugiere y apruebas", icono: "check" },
};

const REGLAS: { icono: NombreIcono; titulo: string; texto: string; href: string }[] = [
  { icono: "pedido", titulo: "Pedir no es recibir", texto: "El stock solo sube cuando registras la recepción, no cuando se envía el pedido.", href: "/compras" },
  { icono: "evaluacion", titulo: "Sin dato no es cero", texto: "Un día sin ventas registradas queda como desconocido para no engañar al modelo.", href: "/panel" },
  { icono: "proveedor", titulo: "Nada se reenvía a ciegas", texto: "Si un envío queda en duda, se verifica antes de volver a mandarlo al proveedor.", href: "/notificaciones" },
  { icono: "automatizacion", titulo: "Todo queda registrado", texto: "Cada paso automático guarda estado, intentos y error para que puedas rastrearlo.", href: "/automatizaciones" },
];

const estiloEtapa = (id: string) => ({ "--etapa": ETAPAS.find((e) => e.id === id)?.color ?? "var(--ma-azul)" }) as CSSProperties;

/** Revela bloques al entrar en pantalla; sin IntersectionObserver se muestran de inmediato. */
function useRevelar() {
  const raiz = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const elementos = raiz.current?.querySelectorAll<HTMLElement>("[data-revelar]") ?? [];
    if (!("IntersectionObserver" in window)) { elementos.forEach((e) => e.classList.add("is-visible")); return; }
    const observador = new IntersectionObserver((entradas) => entradas.forEach((entrada) => {
      if (entrada.isIntersecting) { entrada.target.classList.add("is-visible"); observador.unobserve(entrada.target); }
    }), { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
    elementos.forEach((e) => observador.observe(e));
    return () => observador.disconnect();
  }, []);
  return raiz;
}

function Contenido() {
  const raiz = useRevelar();
  return <div className="fx-page" ref={raiz}>
    <section className="fx-hero">
      <div className="fx-hero-text">
        <span className="ma-stage-chip"><Icono nombre="guia" tamano={14} /> Guía del flujo</span>
        <h1>Cómo funciona <span className="fx-gradient-text">FoodSave</span></h1>
        <p>De las ventas de ayer a los pedidos de mañana. FoodSave predice cuánto vas a vender, calcula qué producir y qué insumos faltan, y se los pide a tus proveedores. Tú solo revisas y decides.</p>
        <ul className="fx-hero-stats">
          <li><strong>6</strong><span>etapas</span></li>
          <li><strong>{PASOS.length}</strong><span>pasos</span></li>
          <li><strong>{PASOS.filter((p) => p.quien !== "auto").length}</strong><span>decisiones tuyas</span></li>
        </ul>
        <div className="fx-hero-actions">
          <a className="button-primary" href="#paso-a-paso">Ver el paso a paso <Icono nombre="flecha-derecha" tamano={18} /></a>
          <Link className="button-secondary" href="/">Ir al Resumen</Link>
        </div>
      </div>
      <div className="fx-orbit" aria-label="Las seis etapas forman un ciclo que se repite cada día">
        <svg className="fx-orbit-ring" viewBox="0 0 400 400" aria-hidden="true">
          <defs>
            <linearGradient id="fx-anillo" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#4285F4" /><stop offset=".35" stopColor="#00BCD4" /><stop offset=".55" stopColor="#FBBC05" /><stop offset=".75" stopColor="#34A853" /><stop offset="1" stopColor="#EA4335" />
            </linearGradient>
          </defs>
          <circle cx="200" cy="200" r="150" className="fx-orbit-track" />
          <circle cx="200" cy="200" r="150" className="fx-orbit-flow" stroke="url(#fx-anillo)" />
          <circle r="7" className="fx-orbit-dot">
            <animateMotion dur="9s" repeatCount="indefinite" path="M200,50 a150,150 0 1,1 -0.1,0" />
          </circle>
          <circle r="4" className="fx-orbit-dot fx-orbit-dot-2">
            <animateMotion dur="9s" begin="-4.5s" repeatCount="indefinite" path="M200,50 a150,150 0 1,1 -0.1,0" />
          </circle>
        </svg>
        <div className="fx-orbit-center"><Icono nombre="chispa" tamano={28} /><strong>Ciclo diario</strong><span>se repite cada día</span></div>
        {ETAPAS_CICLO.map((etapa, i) => <Link key={etapa.id} href={visibles(etapa, true)[0].href} className="fx-orbit-node"
          style={{ ...estiloEtapa(etapa.id), "--angulo": `${i * 60}deg` } as CSSProperties} title={`${etapa.numero}. ${etapa.titulo}: ${etapa.resumen}`}>
          <span className="fx-orbit-bubble"><Icono nombre={visibles(etapa, true)[0].icono} tamano={22} /><span className="ma-stage-number">{etapa.numero}</span></span>
          <span className="fx-orbit-label">{etapa.titulo}</span>
        </Link>)}
      </div>
    </section>

    <section className="fx-section" data-revelar>
      <header className="fx-section-head"><span className="analytics-eyebrow">Vista rápida</span><h2>El ciclo en 6 etapas</h2><p>Cada etapa entrega su resultado a la siguiente. Pulsa una tarjeta para ir a esa parte de FoodSave.</p></header>
      <ol className="fx-pipeline">
        {ETAPAS_CICLO.map((etapa) => <li key={etapa.id} style={estiloEtapa(etapa.id)}>
          <Link href={visibles(etapa, true)[0].href} className="fx-stage-card">
            <span className="fx-stage-top"><span className="ma-stage-number">{etapa.numero}</span><span className="fx-stage-icon"><Icono nombre={visibles(etapa, true)[0].icono} tamano={22} /></span></span>
            <strong>{etapa.titulo}</strong>
            <span className="fx-stage-sum">{etapa.resumen}</span>
            <span className="fx-stage-screens">{visibles(etapa, true).map((p) => p.texto).join(" · ")}</span>
          </Link>
        </li>)}
      </ol>
    </section>

    <section className="fx-section fx-example" data-revelar>
      <header className="fx-section-head"><span className="analytics-eyebrow">Ejemplo</span><h2>Un croissant de punta a punta</h2><p>Así viajan los números por FoodSave en un solo día. Cada dato te lleva a la pantalla donde lo ves.</p></header>
      <ol className="fx-chain">
        {EJEMPLO.map((dato, i) => <li key={dato.texto} style={{ "--i": i } as CSSProperties}>
          <Link href={dato.href} className="fx-chain-item">
            <strong>{dato.valor}</strong><span className="fx-chain-unit">{dato.unidad}</span><small>{dato.texto}</small>
          </Link>
        </li>)}
      </ol>
    </section>

    <section className="fx-section" id="paso-a-paso" data-revelar>
      <header className="fx-section-head"><span className="analytics-eyebrow">Paso a paso</span><h2>Qué pasa en cada momento</h2>
        <p className="fx-legend">{(Object.keys(QUIEN) as Quien[]).map((q) => <span key={q} className={`fx-who is-${q}`}><Icono nombre={QUIEN[q].icono} tamano={14} />{QUIEN[q].texto}</span>)}</p>
      </header>
      <ol className="fx-timeline">
        {PASOS.map((paso, i) => {
          const etapa = ETAPAS.find((e) => e.id === paso.etapa);
          return <li key={paso.titulo} className="fx-step" style={estiloEtapa(paso.etapa)} data-revelar>
            <span className="fx-step-node" aria-hidden="true"><Icono nombre={paso.icono} tamano={20} /></span>
            <article className="fx-step-card">
              <div className="fx-step-meta"><span className="fx-step-num">Paso {i + 1}</span><span className="ma-stage-chip">{etapa?.numero}. {etapa?.titulo}</span><span className={`fx-who is-${paso.quien}`}><Icono nombre={QUIEN[paso.quien].icono} tamano={14} />{QUIEN[paso.quien].texto}</span></div>
              <h3><Link href={paso.destinos[0].href} className="fx-step-link">{paso.titulo}</Link></h3>
              <p>{paso.texto}</p>
              <p className="fx-step-example"><Icono nombre="chispa" tamano={16} /><span><strong>Ejemplo:</strong> {paso.ejemplo}</span></p>
              <div className="fx-step-links">{paso.destinos.map((d) => <Link key={d.href} href={d.href} className="fx-chip-link">{d.texto}<Icono nombre="flecha-derecha" tamano={14} /></Link>)}</div>
            </article>
          </li>;
        })}
      </ol>
    </section>

    <section className="fx-section" data-revelar>
      <header className="fx-section-head"><span className="analytics-eyebrow">Quién hace qué</span><h2>La máquina calcula, tú decides</h2></header>
      <div className="fx-split">
        {(["auto", "tu"] as const).map((q) => <div key={q} className={`fx-split-col is-${q}`}>
          <h3><Icono nombre={QUIEN[q].icono} tamano={22} />{q === "auto" ? "FoodSave lo hace solo" : "Tú das el visto bueno"}</h3>
          <ul>{PASOS.filter((p) => p.quien === q || (q === "tu" && p.quien === "ambos")).map((p) => <li key={p.titulo}>
            <Link href={p.destinos[0].href}><Icono nombre={p.icono} tamano={18} /><span>{p.titulo}</span><Icono nombre="flecha-derecha" tamano={16} /></Link>
          </li>)}</ul>
        </div>)}
      </div>
    </section>

    <section className="fx-section" data-revelar>
      <header className="fx-section-head"><span className="analytics-eyebrow">Reglas de oro</span><h2>Cuatro cosas que conviene saber</h2></header>
      <div className="fx-rules">
        {REGLAS.map((regla) => <Link key={regla.titulo} href={regla.href} className="fx-rule">
          <span className="fx-rule-icon"><Icono nombre={regla.icono} tamano={22} /></span>
          <strong>{regla.titulo}</strong><p>{regla.texto}</p>
          <span className="fx-rule-go">Ver en FoodSave <Icono nombre="flecha-derecha" tamano={16} /></span>
        </Link>)}
      </div>
    </section>

    <section className="fx-cta" data-revelar>
      <div><h2>¿Listo para empezar?</h2><p>El Resumen te dice en qué etapa estás y cuál es tu siguiente paso.</p></div>
      <Link className="button-primary" href="/">Ir al Resumen <Icono nombre="flecha-derecha" tamano={18} /></Link>
    </section>
  </div>;
}

export default function ComoFunciona() {
  return <ProtectedShell titulo="Cómo funciona" descripcion="Infografía del flujo completo del negocio.">{() => <Contenido />}</ProtectedShell>;
}
