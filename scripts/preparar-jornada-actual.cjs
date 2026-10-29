// Jornada autorizada del 28/10 en la aplicación existente. No crea otra instalación.
const fs=require('node:fs'),cp=require('node:child_process'),path=require('node:path');
process.chdir(path.resolve(__dirname,'..'));
const base=['compose','-f','compose.yaml'];
if(fs.existsSync('.tmp/compose.rojas.yaml'))base.push('-f','.tmp/compose.rojas.yaml');
const dir='.tmp/jornada-actual';fs.mkdirSync(dir,{recursive:true});
function docker(args,op={}){return cp.execFileSync('docker',args,{maxBuffer:60e6,...op});}
function paso(args){docker(args,{stdio:['ignore','inherit','inherit']});}
// Mantener la fecha y los datos de esta preparación; reejecutar no reinicia avances.
const dump=path.join(dir,'antes-jornada-20261028.dump');
paso([...base,'stop','worker','beat']);
try {
 if(!fs.existsSync(dump)){
  const datos=docker([...base,'exec','-T','postgres','pg_dump','-U','foodsave','-d','foodsave','--schema=public','-Fc']);
  if(datos.subarray(0,5).toString()!=='PGDMP')throw Error('Respaldo inválido');
  fs.writeFileSync(dump,datos);
  docker(['cp',dump,'savefood_automatizacion-postgres-1:/tmp/antes-jornada-actual.dump']);
  const indice=docker([...base,'exec','-T','postgres','pg_restore','--list','/tmp/antes-jornada-actual.dump'],{encoding:'utf8'});
  if(!indice.includes('alembic_version'))throw Error('Respaldo sin revisión de esquema');
  const fuente=fs.readFileSync('.tmp/huella-integracion-tienda.py','utf8');
  const huella=docker([...base,'exec','-T','api','python','-'],{input:fuente,encoding:'utf8'});
  JSON.parse(huella);fs.writeFileSync(path.join(dir,'tablas-antes.json'),huella);
  const capturar=`import json,os,psycopg\nwith psycopg.connect(os.environ['DATABASE_URL'].replace('postgresql+psycopg://','postgresql://')) as c:\n print(json.dumps({t:c.execute('SELECT coalesce(max(id),0) FROM '+t).fetchone()[0] for t in ['venta_diaria','revision_venta','movimiento_inventario','artefacto_modelo','lote_producto','lote_ingrediente']},sort_keys=True))`;
  fs.writeFileSync(path.join(dir,'ids-antes.json'),docker([...base,'exec','-T','api','python','-'],{input:capturar,encoding:'utf8'}));
  console.log('Respaldo PostgreSQL verificado; se conserva la instalación y su configuración.');
 }
 const ajustes=['-e','PREPARAR_JORNADA_AUTORIZADA=2026-10-28','-v',path.resolve('scripts')+':/herramientas:ro','-v',path.resolve(dir)+':/evidencia'];
 paso([...base,'run','--rm','--no-deps',...ajustes,'worker','python','/herramientas/preparar-jornada.py']);
 paso([...base,'run','--rm','--no-deps',...ajustes,'worker','python','/herramientas/verificar-jornada.py']);
} finally {paso([...base,'up','-d','--no-deps','--no-build','worker','beat']);}
console.log('Jornada lista en FoodSave http://localhost:3100 y tienda http://localhost:3101.');
