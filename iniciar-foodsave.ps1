param(
    [switch]$Build,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
$bloqueoFoodSave = $null
$tieneBloqueoFoodSave = $false
$codigoSalidaFoodSave = 0

try {
    Set-Location -LiteralPath $PSScriptRoot
    $shaFoodSave = [System.Security.Cryptography.SHA256]::Create()
    try {
        $rutaFoodSave = [System.Text.Encoding]::UTF8.GetBytes($PSScriptRoot.ToLowerInvariant())
        $idFoodSave = [System.BitConverter]::ToString($shaFoodSave.ComputeHash($rutaFoodSave)).Replace('-', '')
    } finally {
        $shaFoodSave.Dispose()
    }
    $bloqueoFoodSave = [System.Threading.Mutex]::new($false, "Local\FoodSaveInicio_$idFoodSave")
    try {
        $tieneBloqueoFoodSave = $bloqueoFoodSave.WaitOne(0)
    } catch [System.Threading.AbandonedMutexException] {
        $tieneBloqueoFoodSave = $true
    }
    if (-not $tieneBloqueoFoodSave) {
        Write-Host 'FoodSave ya se esta iniciando en otra ventana. Espera a que termine.'
    } else {
        if (-not (Test-Path -LiteralPath '.env' -PathType Leaf)) {
            throw 'Falta .env. Copia .env.example y configura POSTGRES_PASSWORD y JWT_SECRET.'
        }
        if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
            throw 'Docker no esta instalado o no esta disponible en PATH.'
        }
        $ErrorActionPreference = 'Continue'
        & docker info --format '{{.ServerVersion}}' *> $null
        $codigoDockerFoodSave = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        if ($codigoDockerFoodSave -ne 0) {
            $carpetaDockerFoodSave = Split-Path -Parent (Get-Command docker).Source
            $desktopDockerFoodSave = [System.IO.Path]::GetFullPath((Join-Path $carpetaDockerFoodSave '..\..\Docker Desktop.exe'))
            if (-not (Test-Path -LiteralPath $desktopDockerFoodSave -PathType Leaf)) {
                throw 'Docker no responde. Abre Docker Desktop y espera a que termine de iniciar.'
            }
            Write-Host 'Iniciando Docker Desktop...'
            Start-Process -FilePath $desktopDockerFoodSave -WindowStyle Hidden
            $limiteDockerFoodSave = [DateTime]::UtcNow.AddSeconds(120)
            do {
                Start-Sleep -Seconds 2
                $ErrorActionPreference = 'Continue'
                & docker info --format '{{.ServerVersion}}' *> $null
                $codigoDockerFoodSave = $LASTEXITCODE
                $ErrorActionPreference = 'Stop'
            } while ($codigoDockerFoodSave -ne 0 -and [DateTime]::UtcNow -lt $limiteDockerFoodSave)
            if ($codigoDockerFoodSave -ne 0) {
                throw 'Docker Desktop no termino de iniciar a tiempo. Revisa su ventana y vuelve a abrir FoodSave.'
            }
        }

        $composeFoodSave = @('compose', '-f', 'compose.yaml')
        if (Test-Path -LiteralPath '.tmp/compose.rojas.yaml' -PathType Leaf) {
            $composeFoodSave += @('-f', '.tmp/compose.rojas.yaml')
        }
        $ErrorActionPreference = 'Continue'
        $configuracionFoodSave = & docker @composeFoodSave config --format json
        $codigoConfigFoodSave = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        if ($codigoConfigFoodSave -ne 0) {
            throw 'No se pudo leer la configuracion de Compose. Revisa el error anterior.'
        }
        $configuracionFoodSave = ($configuracionFoodSave -join "`n") | ConvertFrom-Json
        $puertoWebFoodSave = [int]$configuracionFoodSave.services.frontend.ports[0].published
        if ($puertoWebFoodSave -lt 1 -or $puertoWebFoodSave -gt 65535) {
            throw 'Compose no publica un puerto web valido para FoodSave.'
        }
        $urlWebFoodSave = "http://localhost:$puertoWebFoodSave/"
        $opcionesFoodSave = $composeFoodSave + @('up', '-d')
        if ($Build) { $opcionesFoodSave += '--build' }
        Write-Host 'Iniciando FoodSave...'
        $ErrorActionPreference = 'Continue'
        & docker @opcionesFoodSave
        $codigoComposeFoodSave = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        if ($codigoComposeFoodSave -ne 0) {
            throw 'Compose no pudo iniciar FoodSave. Revisa el error anterior. Si hay un conflicto de nombres, espera a que termine cualquier otro arranque y vuelve a intentarlo.'
        }

        Write-Host 'Esperando a que la API y la web respondan...'
        $limiteFoodSave = [DateTime]::UtcNow.AddSeconds(120)
        $listoFoodSave = $false
        do {
            try {
                $apiFoodSave = Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:8000/salud' -TimeoutSec 3
                $webFoodSave = Invoke-WebRequest -UseBasicParsing -Uri $urlWebFoodSave -TimeoutSec 3
                $listoFoodSave = $apiFoodSave.StatusCode -eq 200 -and $webFoodSave.StatusCode -eq 200
            } catch {
                $listoFoodSave = $false
            }
            if (-not $listoFoodSave) { Start-Sleep -Seconds 2 }
        } while (-not $listoFoodSave -and [DateTime]::UtcNow -lt $limiteFoodSave)
        if (-not $listoFoodSave) {
            throw 'Los servicios no respondieron a tiempo. Consulta docker compose ps y docker compose logs --tail 50 api frontend migraciones.'
        }
        if (-not $NoBrowser) {
            Start-Process $urlWebFoodSave
        }
        Write-Host "FoodSave esta listo en $urlWebFoodSave Puedes cerrar esta ventana."
    }
} catch {
    Write-Host ("No se pudo iniciar FoodSave: " + $_.Exception.Message) -ForegroundColor Red
    $codigoSalidaFoodSave = 1
} finally {
    if ($tieneBloqueoFoodSave) { $bloqueoFoodSave.ReleaseMutex() }
    if ($null -ne $bloqueoFoodSave) { $bloqueoFoodSave.Dispose() }
}
exit $codigoSalidaFoodSave
