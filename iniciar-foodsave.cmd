@echo off
setlocal
cd /d "%~dp0"
if not exist ".env" (
  echo Falta .env. Copia .env.example, configura POSTGRES_PASSWORD y JWT_SECRET y vuelve a abrir este archivo.
  pause
  exit /b 1
)
docker compose up -d
if errorlevel 1 (
  echo No se pudo iniciar FoodSave. Comprueba que Docker Desktop este abierto.
  pause
  exit /b 1
)
start "" "http://localhost:3000/inicializacion/piloto"
echo FoodSave esta abierto. Puedes cerrar esta ventana.
