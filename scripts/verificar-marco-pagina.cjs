/* Marco real con React/SSR: encabezado por etapa, recorrido anterior/siguiente, título único y enlaces según rol. Sin API. */
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
const {ETAPAS,ETAPAS_CICLO,ubicar,vecinos}=require('../frontend/src/components/layout/navegacion.tsx');
function render(ruta,extra={}){
  return new JSDOM(renderToStaticMarkup(React.createElement(MarcoPagina,{ruta,titulo:'Inventario',descripcion:'Disponibilidad por lotes.',...extra},React.createElement('section',{'data-prueba':'contenido'},'Contenido del módulo')))).window.document;
}
// Mapa: rutas únicas, seis etapas numeradas en orden y Administración fuera del recorrido.
const rutas=ETAPAS.flatMap(e=>e.pantallas.map(p=>p.href));
assert.equal(new Set(rutas).size,rutas.length,'Cada ruta aparece una sola vez en el menú');
assert.deepEqual(ETAPAS_CICLO.map(e=>e.numero),[1,2,3,4,5,6]);
assert.equal(ubicar('/inventario/lotes/42').pantalla.href,'/inventario','Las rutas de detalle se ubican en su pantalla');
assert.equal(vecinos('/configuracion').siguiente,null,'Administración no forma parte del recorrido');
assert.equal(vecinos('/').siguiente.href,'/inicializacion');
const normal=render('/inventario');
assert.equal(normal.querySelectorAll('h1').length,1);
assert.equal(normal.querySelector('.ma-page-header h1').textContent,'Inventario');
assert.match(normal.querySelector('.ma-stage-chip').textContent,/Paso 4/);
assert.ok(normal.querySelector('.workspace-content [data-prueba="contenido"]'));
assert.equal(normal.querySelector('.ma-pager-next').getAttribute('href'),vecinos('/inventario').siguiente.href);
const inicio=render('/');
assert.equal(inicio.querySelectorAll('.ma-page-header,.ma-pager').length,0,'Inicio dibuja su propio tablero');
assert.ok(inicio.querySelector('[data-prueba="contenido"]'));
const retorno=render('/inventario',{retorno:React.createElement('a',{href:'/automatizaciones','data-prueba':'retorno'},'Continuar automatización')});
assert.equal(retorno.querySelector('[data-prueba="retorno"]').getAttribute('href'),'/automatizaciones');
// ProtectedShell real: Usuarios nunca se sugiere como siguiente paso a un operador.
const {ProtectedShell}=require('../frontend/src/components/layout/ProtectedShell.tsx');
const contextoOriginal=React.useContext;
try {
  for(const rol of ['OPERADOR','ADMINISTRADOR']){
    rutaActual='/configuracion';
    React.useContext=()=>({token:'fixture',perfil:{rol},negocio:{nombre:'Prueba'}});
    const html=renderToStaticMarkup(React.createElement(ProtectedShell,{titulo:'Configuración',descripcion:'Datos del negocio.'},()=>React.createElement('p',null,'Contenido autorizado')));
    const d=new JSDOM(html).window.document;
    assert.equal(d.querySelectorAll('h1').length,1);
    assert.equal(d.querySelectorAll('a[href="/usuarios"]').length,0);
  }
} finally {React.useContext=contextoOriginal;}
console.log('OK marco por etapas: mapa único, encabezado con paso, recorrido anterior/siguiente, Inicio sin duplicar y enlaces según rol. React real, sin API.');
