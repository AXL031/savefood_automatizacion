/* Marco real con React/SSR: navegación contextual, títulos y portadas existentes. Sin API. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),Module=require('node:module');
const raiz=path.resolve(__dirname,'..'),req=Module.createRequire(path.join(raiz,'frontend/package.json'));
const ts=req('typescript'),React=req('react'),{renderToStaticMarkup}=req('react-dom/server'),{JSDOM}=req('jsdom');
for(const ext of ['.ts','.tsx'])require.extensions[ext]=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true},fileName:f}).outputText,f);
const original=Module._load, resolver=Module._resolveFilename;
let rutaActual='/configuracion';
Module._resolveFilename=function(n,...args){return resolver.call(this,n.startsWith('@/')?path.join(raiz,'frontend/src',n.slice(2)):n,...args);};
Module._load=function(nombre,...args){
  if(nombre==='next/link')return {__esModule:true,default:({children,href,...props})=>React.createElement('a',{href,...props},children)};
  if(nombre==='next/navigation')return {usePathname:()=>rutaActual,useRouter:()=>({replace:()=>{}})};
  return original.call(this,nombre,...args);
};
const {MarcoPagina}=require('../frontend/src/components/layout/MarcoPagina.tsx');
const enlaces=[{href:'/ingredientes',texto:'Ingredientes'},{href:'/inventario',texto:'Inventario'}];
function render(ruta,extra={}){
  return new JSDOM(renderToStaticMarkup(React.createElement(MarcoPagina,{ruta,enlaces,grupo:'Catálogo e inventario',titulo:'Inventario',descripcion:'Disponibilidad por lotes.',...extra},React.createElement('section',{'data-prueba':'contenido'},'Contenido del módulo')))).window.document;
}
const normal=render('/inventario');
assert.equal(normal.querySelectorAll('h1').length,1);
assert.equal(normal.querySelector('.workspace-hero h1').textContent,'Inventario');
assert.equal(normal.querySelector('nav[aria-label="Navegación de Catálogo e inventario"] a[aria-current="page"]').getAttribute('href'),'/inventario');
assert.equal(normal.querySelectorAll('a[aria-current="page"]').length,1);
assert.ok(normal.querySelector('.workspace-content [data-prueba="contenido"]'));
const detalle=render('/inventario/lotes/42');
assert.equal(detalle.querySelector('a[aria-current="page"]').getAttribute('href'),'/inventario');
for(const ruta of ['/','/pronosticos','/panel','/informes']){
  const d=render(ruta);
  assert.equal(d.querySelectorAll('.workspace-hero,.workspace-nav').length,0,'Conservar portada/navegación propia de Resultados');
  assert.equal(d.querySelectorAll('h1').length,1);
  assert.ok(d.querySelector('[data-prueba="contenido"]'));
}
assert.equal(render('/configuracion',{enlaces:[]}).querySelectorAll('nav').length,0);
const retorno=render('/inventario',{retorno:React.createElement('a',{href:'/automatizaciones','data-prueba':'retorno'},'Continuar automatización')});
assert.equal(retorno.querySelector('[data-prueba="retorno"]').getAttribute('href'),'/automatizaciones');
// El marco recibe solo enlaces autorizados: comprobar el filtro del ProtectedShell real.
const {ProtectedShell}=require('../frontend/src/components/layout/ProtectedShell.tsx');
const contextoOriginal=React.useContext;
try {
  for(const rol of ['OPERADOR','ADMINISTRADOR']){
    React.useContext=()=>({token:'fixture',perfil:{rol},negocio:{nombre:'Prueba'}});
    const html=renderToStaticMarkup(React.createElement(ProtectedShell,{titulo:'Configuración',descripcion:'Datos del negocio.'},()=>React.createElement('p',null,'Contenido autorizado')));
    const d=new JSDOM(html).window.document;
    assert.equal(d.querySelectorAll('a[href="/usuarios"]').length,rol==='ADMINISTRADOR'?1:0);
    assert.equal(d.querySelector('a[aria-current="page"]').getAttribute('href'),'/configuracion');
  }
} finally {React.useContext=contextoOriginal;}
console.log('OK marco compartido: navegación activa/detalle, título único, contenido/retorno, portadas sin duplicar y enlaces según rol. React real, sin API.');
