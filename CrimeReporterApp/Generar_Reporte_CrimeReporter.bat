@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Ejecutable para generar el reporte usando el script PowerShell del proyecto
REM Colocado dentro de la carpeta del proyecto: CrimeReporterApp

REM Ruta por defecto de entrada (ajústala si prefieres otra carpeta)
REM Buscar .xlsx en subcarpeta "Datos Base" dentro del proyecto
set INPUT_DIR=%~dp0Datos Base
if not exist "%INPUT_DIR%" mkdir "%INPUT_DIR%"
set INPUT_PATTERN=%INPUT_DIR%\*.xlsx

for /f %%i in ('powershell -NoLogo -Command "(Get-Date).ToString('yyyyMMdd-HHmm')"') do set TS=%%i
REM Salida por defecto en la MISMA carpeta del proyecto
set DEFAULT_OUT=%~dp0Reporte_CrimeReporter_!TS!.xlsx

echo ===============================
echo Generar Reporte CrimeReporter
echo ===============================
echo Carpeta de entrada: %INPUT_DIR%
echo Patron de busqueda: %INPUT_PATTERN%
set /p MUNICIPIO=Municipio foco (opcional, ej. Jamundi): 
set /p OUT=Ruta de salida [Enter para %DEFAULT_OUT%]: 
if "!OUT!"=="" set OUT=%DEFAULT_OUT%

echo.
echo Generando reporte...
powershell -ExecutionPolicy Bypass -NoLogo -File "%~dp0run_report.ps1" -In "%INPUT_PATTERN%" -Out "!OUT!" -Municipio "!MUNICIPIO!"
set RC=%ERRORLEVEL%
echo.
if "%RC%"=="0" (
  echo Listo. Archivo creado en: "!OUT!"
) else (
  echo Ocurrio un error. Revisa los mensajes arriba.
)
echo.
pause
endlocal
