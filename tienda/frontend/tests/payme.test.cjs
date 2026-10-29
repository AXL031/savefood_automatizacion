const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const ts = require("typescript");
// Cargar módulos de la aplicación con TypeScript, sin navegador ni peticiones externas.
for (const extension of [".ts", ".tsx"]) {
  require.extensions[extension] = (module, file) => module._compile(ts.transpileModule(fs.readFileSync(file, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true }
  }).outputText, file);
}
const { configuracionFlex, cargarFlex, METODOS_PAYME } = require("../src/tienda/payme.ts");
for (const metodo of ["CARD", "YAPE", "QR", "PAGOEFECTIVO"]) {
  test(`Flex presenta exclusivamente ${metodo}`, () => {
    const config = configuracionFlex({ nonce: "nonce", payload: {}, metodo });
    assert.deepEqual(config.display_settings.methods, [metodo]);
    assert.equal(config.settings.display_result_screen, false);
  });
}
test("renderiza los cuatro botones, sin campos locales de tarjeta", () => {
  const React = require("react");
  const { renderToStaticMarkup } = require("react-dom/server");
  const { PagoPayme } = require("../src/tienda/componentes/PagoPayme.tsx");
  const html = renderToStaticMarkup(React.createElement(PagoPayme, {
    lineas: [], entrega: {}, nombre: "", correo: "", alIntentar: () => true, alAprobar: () => {}, alBloquear: () => {}
  }));
  assert.equal((html.match(/class="t-payme-metodo"/g) || []).length, 4);
  for (const m of METODOS_PAYME) assert.ok(html.includes(m.nombre));
  assert.ok(!/CVV|Número de tarjeta|PLIN_SIMULADO/.test(html));
});
test("impide cargar un SDK de producción u otra URL", async () => {
  await assert.rejects(cargarFlex({ script_url: "https://produccion.example/sdk.js", css_url: "https://produccion.example/sdk.css" }), /ambiente de pruebas/);
});
