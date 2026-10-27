param([switch]$Publico,[switch]$NoBuild,[switch]$Preparar)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$archivoEnv = Join-Path $PSScriptRoot '.env.pruebas'
function Nueva-Clave { $bytes=New-Object byte[] 32; $rng=[System.Security.Cryptography.RandomNumberGenerator]::Create(); try{$rng.GetBytes($bytes)}finally{$rng.Dispose()}; return ([BitConverter]::ToString($bytes)).Replace('-','').ToLowerInvariant() }
if (!(Test-Path -LiteralPath $archivoEnv)) {
  $cuentasDemo=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'datos_carga/cuentas_demo.json') -Raw -Encoding utf8 | ConvertFrom-Json
  $admin=[string]$cuentasDemo.administrador.contrasena; $operador=[string]$cuentasDemo.trabajador.contrasena; $cliente=[string]$cuentasDemo.cliente.contrasena
  foreach($claveDemo in @($admin,$operador,$cliente)){if($claveDemo -notmatch '^[A-Za-z0-9_-]{16,128}$'){throw 'Las claves demo deben tener 16-128 letras, numeros, guiones o guiones bajos.'}}
  if($cuentasDemo.administrador.correo -ne 'admin.foodsave@example.com' -or $cuentasDemo.trabajador.correo -ne 'operador.foodsave@example.com' -or $cuentasDemo.cliente.correo -ne 'cliente.foodsave@example.com'){throw 'Los correos de cuentas_demo.json deben coincidir con la semilla.'}
  $pg=Nueva-Clave; $jwt=Nueva-Clave
  @("POSTGRES_PASSWORD=$pg","JWT_SECRET=$jwt",'PUBLIC_BASE_URL=http://localhost:3100','HABILITAR_CLIENTE_LOCAL=1','HABILITAR_DATOS_PRUEBA=1','HABILITAR_ENLACES_PROVEEDOR=1','NEXT_PUBLIC_TIENDA_MODO=api',"DEMO_ADMIN_PASSWORD=$admin","DEMO_OPERADOR_PASSWORD=$operador","DEMO_CLIENTE_PASSWORD=$cliente") | Set-Content -LiteralPath $archivoEnv -Encoding ascii
  New-Item -ItemType Directory -Path '.tmp' -Force | Out-Null
  @('Cuentas publicas de demostracion: datos_carga/cuentas_demo.json. No usar con datos reales.','Panel: http://localhost:3100/iniciar-sesion',"Admin: admin.foodsave@example.com / $admin", "Trabajador: operador.foodsave@example.com / $operador",'Tienda: http://localhost:3100/tienda',"Cliente local: cliente.foodsave@example.com / $cliente",'Datos sintéticos. Google es opcional y no se suplanta. La carga no envía mensajes.') | Set-Content -LiteralPath '.tmp/credenciales-pruebas.txt' -Encoding utf8
}
if($Preparar){Write-Output 'Configuración privada preparada: .env.pruebas y .tmp/credenciales-pruebas.txt';exit 0}
$argumentos=@('compose','--env-file',$archivoEnv,'-p','foodsave_pruebas','-f','compose.yaml','-f','compose.pruebas.yaml')
if($NoBuild){ & docker @argumentos up -d }else{ & docker @argumentos up --build -d }
if($LASTEXITCODE -ne 0){throw 'Docker no completó el arranque; no se borran volúmenes. Abre Docker Desktop y revisa los mensajes.'}
& docker @argumentos exec -T api python -m app.modules.operaciones.semilla
if($LASTEXITCODE -ne 0){throw 'No se completó la carga aislada. Revisa el error; no se sobrescribe una base existente.'}
Write-Output 'Demo disponible: http://localhost:3100. Credenciales privadas: .tmp/credenciales-pruebas.txt'
if($Publico){
  & docker @argumentos --profile publico up -d --no-deps tunnel
  if($LASTEXITCODE -ne 0){throw 'No se pudo iniciar el túnel gratuito.'}
  $idTunel=(& docker @argumentos ps -q tunnel | Select-Object -First 1)
  if(!$idTunel){throw 'No se encontró el contenedor del túnel.'}
  $inicioTunel=(& docker inspect --format '{{.State.StartedAt}}' $idTunel).Trim()
  $urlPublica=$null
  for($i=0;$i -lt 30;$i++){
    $logs=& docker @argumentos logs --since $inicioTunel --no-color tunnel 2>&1 | Out-String
    $direcciones=[regex]::Matches($logs,'https://[a-z0-9-]+\.trycloudflare\.com')
    if($direcciones.Count -gt 0){$urlPublica=$direcciones[$direcciones.Count-1].Value;break}
    Start-Sleep -Seconds 2
  }
  if(!$urlPublica){Write-Output 'El túnel aún no devolvió URL. Consulta docker compose con los mismos archivos y el perfil publico.';exit 1}
  $lineasEnv=Get-Content -LiteralPath $archivoEnv
  $lineasEnv | ForEach-Object {if($_ -match '^PUBLIC_BASE_URL='){"PUBLIC_BASE_URL=$urlPublica"}else{$_}} | Set-Content -LiteralPath $archivoEnv -Encoding ascii
  New-Item -ItemType Directory -Path '.tmp' -Force | Out-Null
  Set-Content -LiteralPath '.tmp/url-publica.txt' -Value $urlPublica -Encoding ascii
  & docker @argumentos up -d --no-deps --wait api worker
  if($LASTEXITCODE -ne 0){throw 'No se pudo configurar la URL pública del proveedor.'}
  Write-Output "Dirección pública temporal: $urlPublica"
  Write-Output 'Al detener el túnel cambia la dirección. Regenera enlaces pendientes después de reiniciarlo. La PC debe permanecer encendida.'
}
