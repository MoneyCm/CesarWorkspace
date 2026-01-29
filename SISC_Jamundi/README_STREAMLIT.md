# 🚀 Despliegue de SISC Jamundí en Streamlit

Este proyecto centraliza las mejores características de todos los observatorios anteriores en una interfaz moderna y fácil de usar.

## Cómo ejecutar localmente

1.  **Asegúrate de tener Python instalado.**
2.  **Instala las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configura la Base de Datos**:
    Asegúrate de que tu base de datos PostgreSQL de `SISC_Jamundi` esté corriendo (vía Docker o local). La app busca por defecto `postgresql://sisc_user:sisc_password@localhost:5432/sisc_jamundi`.
4.  **Lanza la aplicación**:
    ```bash
    streamlit run streamlit_app.py
    ```

## Estructura
- `streamlit_app.py`: Punto de entrada y bienvenida.
- `pages/0_Dashboard.py`: Indicadores clave (KPIs) y tasas de criminalidad.
- `pages/1_Mapa_Interactivo.py`: Visualización geográfica con Leaflet.
- `pages/2_Ingesta_Datos.py`: Carga y validación de archivos Excel.

## Ventajas
- **Todo en uno**: Ya no necesitas correr backend y frontend por separado.
- **KPIs Automáticos**: Cálculos de tasas por 100k habitantes integrados.
- **Portabilidad**: Listo para ser desplegado en Streamlit Cloud o Railway.
