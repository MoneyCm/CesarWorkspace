import pandas as pd
from datetime import date, timedelta
import random

# Crear datos de ejemplo
datos = []
delitos = ["Hurto a Personas", "Homicidio", "Lesiones Personales", "Violencia Intrafamiliar", "Hurto a Residencias"]
barrios = ["Centro", "San Juan", "Villa del Prado", "La Esmeralda", "El Prado", "Los Andes", "Villa Colombia"]
municipios = ["Jamundí", "Jamundí", "Jamundí", "Jamundí", "Jamundí"]

# Generar datos para los últimos 6 meses
fecha_inicio = date(2024, 1, 1)
fecha_fin = date(2024, 6, 30)

for i in range(50):  # 50 registros de ejemplo
    fecha = fecha_inicio + timedelta(days=random.randint(0, (fecha_fin - fecha_inicio).days))
    
    # Coordenadas aproximadas de Jamundí
    lat_base = 3.262
    lon_base = -76.540
    lat = lat_base + random.uniform(-0.01, 0.01)
    lon = lon_base + random.uniform(-0.01, 0.01)
    
    datos.append({
        'fecha': fecha,
        'delito': random.choice(delitos),
        'barrio': random.choice(barrios),
        'municipio': random.choice(municipios),
        'latitud': lat,
        'longitud': lon,
        'zona': random.choice(['Urbano', 'Rural']),
        'genero_victima': random.choice(['Masculino', 'Femenino']),
        'edad_victima': random.randint(18, 70),
        'arma': random.choice(['Arma de Fuego', 'Arma Blanca', 'Sin Arma', 'Contundente']),
        'modalidad': random.choice(['Individual', 'Grupal', 'Organizada'])
    })

# Crear DataFrame
df = pd.DataFrame(datos)

# Guardar como Excel
df.to_excel('datos_ejemplo.xlsx', index=False)
print("Archivo 'datos_ejemplo.xlsx' creado exitosamente!")
print(f"Se generaron {len(datos)} registros de ejemplo")
print("\nColumnas incluidas:")
for col in df.columns:
    print(f"- {col}")


