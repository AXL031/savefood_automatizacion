const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),ts=require('typescript'),{JSDOM}=require('jsdom');
for(const ext of ['.ts','.tsx'])require.extensions[ext]=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true}}).outputText,f);
const pago=require('../src/tienda/payme.ts');
const comprador={nombres:'Persona',apellidos:'Prueba',correo:'persona@example.com'};
const entrega={nombre_receptor:'Persona Prueba',direccion:'Calle ficticia 123',distrito:'Lima',celular:'999111222',referencia:''};
const cot={origen:'d0fc5983-c6e3-41ad-bf65-dd05dcc12c07',huella:'a'.repeat(64),total:'6.00',lineas:[],moneda:'PEN'};
function entorno(){const dom=new JSDOM('',{url:'http://localhost:3101/tienda/carrito'});global.localStorage=dom.window.localStorage;return dom;}
function r(datos,status=200){return {ok:status<400,status,json:async()=>status<400?{datos}:{error:{mensaje:'No encontrada'}}};}
function vista(){return {id:'id-qa',operacion:'123456789012',metodo:'CARD',estado:'CREADO',pagado:false,total:'6.00',moneda:'PEN',transaction_id:null,
    comercial:{origen:'FOODSAVE',estado:'RESERVADA',ticket:null,reserva_vence_en:null,mensaje:null}};}

test('respuesta perdida se recupera por capacidad y cambiar método usa la cotización original',async()=>{
 const dom=entorno();let registrado=false,perder=true,cuerpos=[];
 global.fetch=async(url,opt={})=>{
  if(String(url).endsWith('/recuperar'))return registrado?r(vista()):r(null,404);
  const b=JSON.parse(opt.body);cuerpos.push(b);registrado=true;
  if(perder){perder=false;throw new TypeError('Timeout después de guardar');}
  return r({pago:{...vista(),metodo:b.metodo},flex:null});
 };
 try{
  await assert.rejects(pago.iniciarPayme('CARD',[{producto_id:101,cantidad:2}],comprador,entrega,cot),/Timeout/);
  const rec=await pago.recuperarPagoPendiente();assert.equal(rec.id,'id-qa');
  assert.equal(pago.referenciasPayme().length,1);
  await pago.reabrirPayme('YAPE');
  assert.equal(cuerpos[0].clave_checkout,cuerpos[1].clave_checkout);
  assert.equal(cuerpos[1].origen_catalogo,cot.origen);assert.equal(cuerpos[1].cotizacion_hash,cot.huella);assert.equal(cuerpos[1].total_revisado,'6.00');
  await assert.rejects(pago.iniciarPayme('QR',[{producto_id:202,cantidad:1}],comprador,entrega,{...cot,total:'3.00'}),/operación pendiente/);
  assert.equal(cuerpos.length,2,'No iniciar otro pago ante un pendiente recuperado');
 }finally{dom.window.close();}
});

test('la recuperación del registro comercial usa la capacidad del pago, sin datos de tarjeta',async()=>{
 const dom=entorno();let solicitud;
 try{
  pago.recordarPago(vista(),'capacidad-privada-qa');
  global.fetch=async(url,opt)=>{solicitud={url,opt};return r({...vista(),pagado:true,comercial:{...vista().comercial,estado:'REGISTRADA',ticket:{ticket_id:1,numero:'V-00000001',total:'6.00'}}});};
  const p=await pago.sincronizarVentaPayme('id-qa');
  assert.equal(p.comercial.estado,'REGISTRADA');assert.equal(solicitud.opt.headers.Authorization,'Bearer capacidad-privada-qa');
  assert.ok(String(solicitud.url).endsWith('/id-qa/sincronizar'));assert.equal(solicitud.opt.body,undefined);
  assert.equal(pago.referenciasPayme()[0].comercial.ticket.numero,'V-00000001');
 }finally{dom.window.close();}
});
