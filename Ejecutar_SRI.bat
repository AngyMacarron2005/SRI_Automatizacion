
@echo off
setlocal
title Robot SRI - Finetic C.L.

cd /d "%~dp0"

:: Si el EXE llama al BAT, solo preparar Chrome
if /i "%~1"=="PREPARAR" goto PREPARAR_CHROME

echo ==========================================
echo       ROBOT SRI - FINETIC C.L.
echo ==========================================
echo.

:: Buscar Google Chrome
set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"

if not exist "%CHROME%" (
    set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
)

if not exist "%CHROME%" (
    echo ERROR: No se encontro Google Chrome.
    pause
    exit /b 1
)

:: Perfil exclusivo del SRI
set "PROFILE=%LOCALAPPDATA%\SRI_Chrome_Debug"

:: Comprobar Chrome
echo [1/3] Comprobando Google Chrome...

powershell -NoProfile -Command ^
 "try { $r=Invoke-RestMethod 'http://127.0.0.1:9222/json/version' -TimeoutSec 2; if($r.Browser -like 'Chrome/*' -and $r.webSocketDebuggerUrl){exit 0} } catch {}; exit 1"

if errorlevel 1 (
    echo [2/3] Iniciando Chrome...

    start "" "%CHROME%" ^
        --remote-debugging-port=9222 ^
        --user-data-dir="%PROFILE%" ^
        --new-window ^
        "https://srienlinea.sri.gob.ec/"
) else (
    echo [2/3] Chrome ya esta preparado.
)

:PREPARAR_CHROME

:: Esperar a que Chrome este disponible
echo.
echo Esperando conexion con Chrome...

powershell -NoProfile -Command ^
 "$ok=$false; for($i=0;$i-lt 30;$i++){try{$r=Invoke-RestMethod 'http://127.0.0.1:9222/json/version' -TimeoutSec 2; if($r.Browser -like 'Chrome/*' -and $r.webSocketDebuggerUrl){$ok=$true;break}}catch{}; Start-Sleep -Seconds 1}; if($ok){exit 0}else{exit 1}"

if errorlevel 1 (
    echo ERROR: Chrome no pudo iniciar correctamente.
    exit /b 1
)

:: Si fue llamado para preparar Chrome, regresar al EXE
if /i "%~1"=="PREPARAR" exit /b 0

:: Ejecutar el EXE
echo.
echo [3/3] Iniciando automatizacion...
echo.

set "EXE=%~dp0Robot_SRI.exe"

if not exist "%EXE%" (
    echo ERROR: No se encontro Robot_SRI.exe.
    pause
    exit /b 1
)

"%EXE%" --ejecutar

echo.
echo ==========================================
echo       PROGRAMA FINALIZADO
echo ==========================================
pause

endlocal
