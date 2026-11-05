// Coordinación Cueva. Jornada expresamente solicitada el 04/11, instalación existente.
// No envía Telegram ni inicia pagos. --respaldo prepara solo la recuperación previa.
const fs=require('node:fs'),cp=require('node:child_process'),path=require('node:path'),crypto=require('node:crypto');
process.chdir(path.resolve(__dirname,'..'));
const base=['compose','-f','compose.yaml'];
if(fs.existsSync('.tmp/compose.rojas.yaml'))base.push('-f','.tmp/compose.rojas.yaml');
const dir=path.resolve('.tmp/demo-2026-11-04');fs.mkdirSync(dir,{recursive:true});
function docker(args,options={}) { return cp.execFileSync('docker',args,{maxBuffer:100e6,...options}); }
function paso(args) { docker(args,{stdio:['ignore','inherit','inherit']}); }
function guardar(nombre,contenido) { fs.writeFileSync(path.join(dir,nombre),contenido); }
const dump=path.join(dir,'antes-demo.dump');
if(!fs.existsSync(path.join(dir,'respaldo-verificado.json'))) {
  // La aplicación sigue consultable; se detienen los productores durante el respaldo.
  paso([...base,'stop','worker','beat','comercio']);
  try {
    const datos=docker([...base,'exec','-T','postgres','pg_dump','-U','foodsave','-d','foodsave','--schema=public','-Fc']);
    if(datos.subarray(0,5).toString()!=='PGDMP')throw Error('Respaldo PostgreSQL inválido');
    guardar('antes-demo.dump',datos);
    const pg=docker([...base,'ps','-q','postgres'],{encoding:'utf8'}).trim();
    docker(['cp',dump,pg+':/tmp/antes-demo-noviembre.dump']);
    const indice=docker([...base,'exec','-T','postgres','pg_restore','--list','/tmp/antes-demo-noviembre.dump'],{encoding:'utf8'});
    if(!indice.includes('alembic_version'))throw Error('Respaldo sin esquema');
    guardar('indice-respaldo.txt',indice);
    guardar('modelos-antes.tar',docker([...base,'exec','-T','api','tar','-cf','-','-C','/code','model_artifacts']));
    const huellas={};
    for(const archivo of ['.env','tienda/.env'])huellas[archivo]=crypto.createHash('sha256').update(fs.readFileSync(archivo)).digest('hex');
    guardar('respaldo-verificado.json',JSON.stringify({fecha:new Date().toISOString(),sha256:crypto.createHash('sha256').update(datos).digest('hex'),huellas_env:huellas},null,2));
    console.log('Respaldo PostgreSQL e índice verificados; modelos anteriores conservados.');
  } finally { paso([...base,'up','-d','--no-deps','--no-build','worker','beat','comercio']); }
}
if(process.argv.includes('--respaldo'))process.exit(0);
paso([...base,'stop','worker','beat']);
try {
  const opciones=['-e','PREPARAR_JORNADA_AUTORIZADA=2026-11-04','-e','PYTHONPATH=/code','-v',path.resolve('scripts')+':/herramientas:ro','-v',dir+':/evidencia'];
  if(!process.argv.includes('--verificar'))paso([...base,'run','--rm','--no-deps',...opciones,'worker','python','/herramientas/preparar-jornada.py',...(process.argv.includes('--reentrenar')?['--reentrenar']:[])]);
  paso([...base,'run','--rm','--no-deps',...opciones,'worker','python','/herramientas/verificar-jornada.py']);
} finally { paso([...base,'up','-d','--no-deps','--no-build','worker','beat']); }
console.log('Preparación y ensayo terminados. Ver .tmp/demo-2026-11-04/escenario.json.');
