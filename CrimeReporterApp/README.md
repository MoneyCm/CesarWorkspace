
# Reportador de Delitos (Excel) — Streamlit

Aplicación ligera para **leer archivos Excel** (SIEDCO/DIJIN y similares) y **generar reportes** por año, mes, departamento, municipio, género, arma/medio y tipo de delito. Funciona en **Windows** y **macOS** con Python.

## ✅ ¿Qué hace?
- Acepta **múltiples .xlsx** arrastrando y soltando.
- Detecta automáticamente la **fila de encabezado** (busca "DEPARTAMENTO" y "MUNICIPIO").
- Limpia y normaliza nombres de **municipio** (remueve "(CT)", corrige acentos comunes).
- Calcula **AÑO** y **MES** desde la fecha.
- Muestra tablas claves y permite **exportar un Excel** con varias pestañas (Por_Mes, Por_Ubicacion, Por_Genero, Por_Arma, Por_Delito…).

## 🚀 Cómo ejecutar (fácil)
1) Instale Python 3.9+ desde https://www.python.org/ (añada "Add to PATH" en Windows).
2) Abra una terminal en esta carpeta y ejecute:
```
pip install -r requirements.txt
streamlit run app.py
```
3) Se abrirá en el navegador (por defecto http://localhost:8501). Cargue sus Excel y ¡listo!

## 📦 Crear ejecutable para Windows (opcional)
Puede empacarlo con **PyInstaller** en un solo .exe:
```
pip install pyinstaller
pyinstaller --onefile --noconsole --add-data "report_engine.py;." app.py
```
> El .exe quedará en `dist/`. Para Streamlit, una alternativa práctica es usar **auto-py-to-exe** o crear un **wrapper** CLI (consulte abajo).

### Opción CLI (sin Streamlit)
Si prefiere una herramienta de línea de comandos:
```
python cli_report.py --in carpeta_o_archivos/*.xlsx --out Reporte.xlsx --municipio "Jamundí"
```
También puede compilar este script a .exe con PyInstaller:
```
pyinstaller --onefile cli_report.py
```

## 🧪 Archivos de prueba
Incluya algunos .xlsx reales en una carpeta y úselos para validar. La app ya detecta encabezados y columnas típicas: `DEPARTAMENTO, MUNICIPIO, FECHA HECHO, CANTIDAD, GENERO, ARMAS MEDIOS, DELITOS` (si existen).

## 🛠️ Soporte y ajustes
- Si su columna de fecha no se llama `FECHA HECHO`, cámbiela en “Opciones” dentro de la app.
- Si sus municipios tienen sufijos “(CT)”, la app puede **normalizarlos**.
- Para agregar nuevas tablas/pivotes, edite `report_engine.py`.

---

Hecho para funcionar **en cualquier PC** con Python. Si desea un instalador “doble‑click” sin requisitos, se puede preparar con PyInstaller/NSIS; dígame y le genero el instalador listo.
