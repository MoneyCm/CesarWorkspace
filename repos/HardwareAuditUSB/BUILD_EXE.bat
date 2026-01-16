@echo off
title Generador de HardwareAudit USB
echo ==========================================
echo      Instalador y Constructor de EXE
echo ==========================================
echo.

echo [1/4] Verificando instalacion de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado.
    echo Por favor instala Python desde https://www.python.org/downloads/
    echo Asegurate de marcar la casilla "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b
)
echo Python detectado correctamente.
echo.

echo [2/4] Instalando librerias necesarias...
python -m pip install -r requirements.txt --quiet
python -m pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Fallo instalando dependencias. Revisa tu conexion a internet.
    pause
    exit /b
)
echo Librerias instaladas.
echo.

echo [3/4] Generando ejecutable (esto puede tardar unos minutos)...
REM --collect-all customtkinter asegura que se incluyan los temas y archivos json
python -m PyInstaller --noconsole --onefile --collect-all customtkinter --name "HardwareAuditUSB" main.py
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller fallo.
    pause
    exit /b
)
echo.

echo [4/4] !Proceso terminado!
echo.
echo Tu aplicacion ejecutable esta lista en la carpeta "dist".
echo Se abrira la carpeta automaticamente.
echo.
explorer dist
pause
