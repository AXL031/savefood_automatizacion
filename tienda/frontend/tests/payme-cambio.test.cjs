const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const ts = require("typescript");
const { JSDOM } = require("jsdom");
for (const extension of [".ts", ".tsx"]) {
  require.extensions[extension] = (module, file) => module._compile(ts.transpileModule(fs.readFileSync(file, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true }
  }).outputText, file);
}
const React = require("react");
const { act } = React;
const { createRoot } = require("react-dom/client");
const { PagoPayme } = require("../src/tienda/componentes/PagoPayme.tsx");
const { puedeCambiarMetodo } = require("../src/tienda/payme.ts");
const nombres = { CARD: "Tarjetas", YAPE: "Yape", QR: "QR billeteras", PAGOEFECTIVO: "PagoEfectivo" };
const pagar = (metodo = "CARD", estado = "CREADO", tid = null) => ({
  id: "pago-de-prueba", operacion: "123456789012", metodo, estado, transaction_id: tid,
  pagado: estado === "AUTORIZADO", total: "9.10", ambiente: "pruebas", moneda: "PEN",
  cotizacion: { lineas: [], total: "9.10", moneda: "PEN" }, creado_en: "2026-10-21T12:00:00Z", continuacion: {}
});

async function montar() {
  const dom = new JSDOM('<!doctype html><div id="raiz"></div>', { url: "http://localhost:3101/tienda/carrito" });
  global.window = dom.window; global.self = dom.window; global.document = dom.window.document; global.localStorage = dom.window.localStorage;
  global.ResizeObserver = class { observe() {} disconnect() {} };
  global.IS_REACT_ACT_ENVIRONMENT = true;
  const fetchOriginal = global.fetch;
  const solicitudes = [], eventos = [], instancias = [], aprobados = [];
  let actual = pagar(), fallo = false, resultado = null;
  class Flex {
    constructor(config) { this.config = config; this.terminaciones = 0; instancias.push(this); }
    init(contenedor, respuesta, tracking, error) {
      this.respuesta = respuesta; this.error = error;
      contenedor.textContent = `Flex ${this.config.display_settings.methods[0]}`;
      eventos.push(`montar:${this.config.display_settings.methods[0]}`);
    }
    terminate() { this.terminaciones++; eventos.push(`cerrar:${this.config.display_settings.methods[0]}`); }
  }
  dom.window.FlexPaymentForms = Flex;
  global.fetch = async (url, opciones = {}) => {
    const cuerpo = opciones.body ? JSON.parse(opciones.body) : null;
    solicitudes.push({ url, cuerpo });
    if (url.endsWith("/configuracion")) return Response.json({ datos: { configurado: true } });
    if (url.endsWith("/verificar")) {
      if (resultado) actual = resultado;
      return Response.json({ datos: actual });
    }
    assert.ok(url.endsWith("/api/v1/pagos"), "No deben ejecutarse otras peticiones ni contactar a Payme");
    eventos.push(`preparar:${cuerpo.metodo}`);
    if (fallo) { fallo = false; return Response.json({ error: { mensaje: "Error de nonce simulado" } }, { status: 502 }); }
    actual = pagar(cuerpo.metodo);
    return Response.json({ datos: { pago: actual, flex: { nonce: "nonce-simulado", payload: {}, metodo: cuerpo.metodo,
      script_url: "https://flex.dev.pay-me.cloud/flex-payment-forms.min.js", css_url: "https://flex.dev.pay-me.cloud/main-flex-payment-forms.css" } } });
  };
  const root = createRoot(dom.window.document.getElementById("raiz"));
  await act(async () => { root.render(React.createElement(PagoPayme, {
    lineas: [{ producto_id: 1, cantidad: 2 }], entrega: { celular: "987654321" }, nombre: "Cliente Prueba", correo: "cliente@example.com",
    alIntentar: () => true, alAprobar: id => aprobados.push(id), alBloquear: () => {}
  })); });
  const boton = metodo => [...document.querySelectorAll(".t-payme-metodo")].find(b => b.querySelector("strong").textContent === nombres[metodo]);
  return { solicitudes, eventos, instancias, aprobados, boton,
    async elegir(metodo) { assert.equal(boton(metodo).disabled, false); await act(async () => { boton(metodo).click(); }); },
    fallarNonce() { fallo = true; },
    resultado(pago) { resultado = pago; },
    async cerrar() { await act(async () => root.unmount()); dom.window.close(); global.fetch = fetchOriginal; }
  };
}

test("cambiar entre los cuatro métodos conserva la clave y desmonta primero el SDK previo", async () => {
  const ui = await montar();
  try {
    for (const metodo of ["CARD", "YAPE", "QR", "PAGOEFECTIVO", "CARD"]) {
      await ui.elegir(metodo);
      for (const otro of Object.keys(nombres)) assert.equal(ui.boton(otro).disabled, false);
      assert.equal(ui.boton(metodo).getAttribute("aria-pressed"), "true");
    }
    assert.deepEqual(ui.instancias.map(i => i.config.display_settings.methods), [["CARD"], ["YAPE"], ["QR"], ["PAGOEFECTIVO"], ["CARD"]]);
    assert.equal(new Set(ui.solicitudes.filter(r => r.cuerpo?.clave_checkout).map(r => r.cuerpo.clave_checkout)).size, 1);
    assert.ok(ui.eventos.indexOf("cerrar:CARD") < ui.eventos.indexOf("preparar:YAPE"));
    assert.ok(ui.instancias.slice(0, -1).every(i => i.terminaciones === 1));
    assert.deepEqual(ui.aprobados, []);
  } finally { await ui.cerrar(); }
});

test("cerrar Flex permite seleccionar otro botón sin borrar la operación", async () => {
  const ui = await montar();
  try {
    await ui.elegir("CARD");
    await act(async () => ui.instancias[0].error("cerro el carrito"));
    await ui.elegir("YAPE");
    assert.equal(ui.instancias[0].terminaciones, 1);
    assert.equal(ui.solicitudes.filter(r => r.cuerpo?.clave_checkout).length, 2);
    assert.equal(ui.boton("CARD").disabled, false);
  } finally { await ui.cerrar(); }
});

test("un error al preparar otro método no deja bloqueados los botones", async () => {
  const ui = await montar();
  try {
    await ui.elegir("CARD"); ui.fallarNonce(); await ui.elegir("YAPE");
    assert.match(document.body.textContent, /Error de nonce simulado/);
    await ui.elegir("QR");
    const claves = ui.solicitudes.filter(r => r.cuerpo?.clave_checkout).map(r => r.cuerpo.clave_checkout);
    assert.equal(new Set(claves).size, 1);
    assert.deepEqual(ui.instancias.map(i => i.config.display_settings.methods), [["CARD"], ["QR"]]);
  } finally { await ui.cerrar(); }
});

test("una respuesta tardía se verifica y cierra el formulario del otro método", async () => {
  const ui = await montar();
  try {
    await ui.elegir("CARD"); await ui.elegir("YAPE");
    ui.resultado(pagar("CARD", "PENDIENTE", "tx-tardia"));
    await act(async () => ui.instancias[0].respuesta({ transaction: { transaction_id: "tx-tardia", state: "AUTORIZADO" } }));
    assert.equal(ui.boton("YAPE").disabled, true);
    assert.equal(ui.instancias[1].terminaciones, 1);
    assert.equal(ui.boton("CARD").disabled, false);
    assert.match(ui.boton("CARD").textContent, /Consultar estado/);
    assert.deepEqual(ui.aprobados, []); // El callback decía aprobado; el backend confirma PENDIENTE.
  } finally { await ui.cerrar(); }
});

test("la política distingue preparación, respuesta incierta y transacción registrada", () => {
  assert.equal(puedeCambiarMetodo(null), true);
  assert.equal(puedeCambiarMetodo(pagar()), true);
  assert.equal(puedeCambiarMetodo(pagar(), true), false);
  assert.equal(puedeCambiarMetodo(pagar("CARD", "CREADO", "tx")), false);
  for (const estado of ["PENDIENTE", "REGISTRADO", "AUTORIZADO", "CANCELADO"]) assert.equal(puedeCambiarMetodo(pagar("QR", estado)), false);
});
