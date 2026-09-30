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
            throw 'Docker no responde. Abre Docker Desktop y espera a que termine de iniciar.'
        }

        $opcionesFoodSave = @('compose', 'up', '-d')
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
                $webFoodSave = Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:3000/inicializacion/piloto' -TimeoutSec 3
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
            Start-Process 'http://localhost:3000/inicializacion/piloto'
        }
        Write-Host 'FoodSave esta listo en http://localhost:3000. Puedes cerrar esta ventana.'
    }
} catch {
    Write-Host ("No se pudo iniciar FoodSave: " + $_.Exception.Message) -ForegroundColor Red
    $codigoSalidaFoodSave = 1
} finally {
    if ($tieneBloqueoFoodSave) { $bloqueoFoodSave.ReleaseMutex() }
    if ($null -ne $bloqueoFoodSave) { $bloqueoFoodSave.Dispose() }
}
exit $codigoSalidaFoodSave
