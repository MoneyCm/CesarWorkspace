from sqlalchemy.orm import Session
from db.models import SessionLocal, Event, EventType, Role, User
from datetime import date, time
import uuid

def seed():
    db = SessionLocal()
    try:
        # Asegurarse de que existan los tipos de eventos básicos
        homicidio = db.query(EventType).filter(EventType.category == "HOMICIDIO").first()
        if not homicidio:
            homicidio = EventType(category="HOMICIDIO", subcategory="DOLOSO", is_delicto=True)
            db.add(homicidio)
            db.commit()
            db.refresh(homicidio)
        
        # Insertar algunos eventos de prueba para el año 2024 con coordenadas en Jamundí
        # Jamundí aprox: 3.26, -76.54
        eventos_prueba = [
            {
                "date": date(2024, 1, 15),
                "time": time(22, 30),
                "ext_id": "POL-001",
                "geom": "POINT(-76.538 3.262)" # Sector céntrico
            },
            {
                "date": date(2024, 2, 20),
                "time": time(14, 00),
                "ext_id": "POL-002",
                "geom": "POINT(-76.545 3.255)" # Sector Sur
            },
            {
                "date": date(2024, 3, 5),
                "time": time(3, 15),
                "ext_id": "POL-003",
                "geom": "POINT(-76.525 3.270)" # Sector Norte
            }
        ]
        
        for ep in eventos_prueba:
            ev = Event(
                occurrence_date=ep["date"],
                occurrence_time=ep["time"],
                event_type_id=homicidio.id,
                external_id=ep["ext_id"]
            )
            db.add(ev)
            db.flush() # para obtener el ID si fuera necesario
            
            # Actualizar la geometría usando SQL crudo
            db.execute(
                func.text("UPDATE events SET location_geom = ST_GeomFromText(:wkt, 4326) WHERE id = :id"),
                {"wkt": ep["geom"], "id": ev.id}
            )
        
        db.commit()
        print("¡Datos de prueba insertados con éxito!")
        
    except Exception as e:
        print(f"Error insertando datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
