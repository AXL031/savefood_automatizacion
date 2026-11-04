/* Formulario real con API falsa: abrir, editar, cancelar, guardar y permisos. Sin red. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),Module=require('node:module');
const raiz=path.resolve(__dirname,'..'),req=Module.createRequire(path.join(raiz,'frontend/package.json'));
const {JSDOM}=req('jsdom'),dom=new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>',{url:'http://avisos.test/'});
Object.assign(global,{window:dom.window,document:dom.window.document,HTMLElement:dom.window.HTMLElement,IS_REACT_ACT_ENVIRONMENT:true});
Object.defineProperty(global,'navigator',{value:dom.window.navigator,configurable:true});
const React=req('react'),{act}=React,{createRoot}=req('react-dom/client'),ts=req('typescript');
for(const ext of ['.ts','.tsx'])require.extensions[ext]=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true},fileName:f}).outputText,f);
const resolve=Module._resolveFilename,load=Module._load;
let rol='ADMINISTRADOR',resolucion=null,llamadas=[];
Module._resolveFilename=function(n,...a){return resolve.call(this,n.startsWith('@/')?path.join(raiz,'frontend/src',n.slice(2)):n,...a);};
Module._load=function(n,...a){
 if(n==='next/link')return {__esModule:true,default:({children,href,...p})=>React.createElement('a',{href,...p},children)};
 if(n==='@/components/layout/ProtectedShell')return {ProtectedShell:({children})=>children({token:'fixture',perfil:{rol}})};
 if(n==='@/services/http')return {solicitar:async(ruta,op)=>{llamadas.push({ruta,...op});if(op.method==='PATCH'){resolucion=op.body.resolucion;return {}; }return [{id:1,titulo:'Promoción sugerida pendiente de aprobación',leido:true,resolucion,creado_en:'2026-10-28T21:55:01Z',datos:{}}];}};
 return load.call(this,n,...a);
};
const Pagina=require('../frontend/src/app/notificaciones/page.tsx').default;
const pausa=()=>new Promise(r=>setTimeout(r,0));
async function ejecutar(fn){await act(async()=>{fn?.();await pausa();await pausa();});}
function boton(t){const b=[...document.querySelectorAll('button')].find(x=>x.textContent===t);assert.ok(b,'Falta botón '+t);return b;}
async function click(t){await ejecutar(()=>boton(t).click());}
async function escribir(texto){const el=document.querySelector('textarea');await ejecutar(()=>{Object.getOwnPropertyDescriptor(dom.window.HTMLTextAreaElement.prototype,'value').set.call(el,texto);el.dispatchEvent(new dom.window.Event('input',{bubbles:true}));});}
(async()=>{
 const root=createRoot(document.getElementById('root'));
 await ejecutar(()=>root.render(React.createElement(Pagina)));
 await click('Registrar resolución');
 const t=document.querySelector('textarea');assert.ok(t.required&&t.minLength===5&&t.maxLength===1000);
 assert.equal(document.querySelector(`label[for="${t.id}"]`).textContent,'Acuerdo o acción interna');
 assert.ok(t.closest('form').classList.contains('operation-form'));
 await escribir('Acuerdo de prueba, sin efectos externos.');await click('Cancelar');
 assert.equal(llamadas.filter(x=>x.method==='PATCH').length,0);
 await click('Registrar resolución');assert.equal(document.querySelector('textarea').value,'');
 await escribir('Revisión interna de prueba.');
 await ejecutar(()=>document.querySelector('form').dispatchEvent(new dom.window.Event('submit',{bubbles:true,cancelable:true})));
 assert.deepEqual(llamadas.filter(x=>x.method==='PATCH').map(x=>x.body),[{leido:true,resolucion:'Revisión interna de prueba.'}]);
 assert.equal(document.querySelector('textarea'),null);assert.ok(document.body.textContent.includes('Revisión interna de prueba.'));
 rol='OPERADOR';llamadas=[];
 await ejecutar(()=>root.render(React.createElement(Pagina,{key:rol})));
 assert.equal(llamadas.length,0);assert.equal(document.querySelector('form'),null);
 assert.ok(document.body.textContent.includes('administrador'));
 await ejecutar(()=>root.unmount());
 console.log('OK avisos: etiqueta asociada, límites conservados, cancelar sin guardar, reapertura limpia, guardado habitual y permisos. React real/API falsa.');
})().catch(e=>{console.error(e);process.exitCode=1;});
