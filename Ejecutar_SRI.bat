@echo off
setlocal
title ROBOT SRI Y ODOO - FINETIC C.L.

cd /d "%~dp0"

echo ==========================================
echo      ROBOT SRI Y ODOO - FINETIC C.L.
echo ==========================================
echo.

:: Comprobar ejecutables
if not exist "%~dp0Robot_SRI.exe" (
    echo ERROR: No se encontro Robot_SRI.exe.
    pause
    exit /b 1
)

if not exist "%~dp0Robot_Odoo.exe" (
    echo ERROR: No se encontro Robot_Odoo.exe.
    pause
    exit /b 1
)

:: Iniciar Chrome si no está abierto (tu lógica actual)
set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"

set "PROFILE=%LOCALAPPDATA%\SRI_Chrome_Debug"

echo [1/4] Comprobando Google Chrome...
powershell -NoProfile -Command "try { $r=Invoke-RestMethod 'http://127.0.0.1:9222/json/version' -TimeoutSec 2; if($r.Browser){exit 0} } catch {}; exit 1"

if errorlevel 1 (
    echo [2/4] Iniciando Chrome...
    start "" "%CHROME%" --remote-debugging-port=9222 --user-data-dir="%PROFILE%" --new-window "https://srienlinea.sri.gob.ec/"
) else (
    echo [2/4] Chrome ya esta preparado.
)

echo Esperando conexion con Chrome...
timeout /t 3 /nobreak > nul

:: Ejecutar paso 1: Robot SRI
echo.
echo [3/4] Ejecutando Robot SRI...
start /wait "" "%~dp0Robot_SRI.exe"

:: Ejecutar paso 2: Robot Odoo
echo.
echo [4/4] Subiendo archivos a Odoo...
start /wait "" "%~dp0Robot_Odoo.exe"

echo.
echo ==========================================
echo      PROGRAMA FINALIZADO CON EXITO
echo ==========================================
pause
endlocal