import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sisc_user:sisc_pass@db:5432/sisc_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    # create tables from schema.sql
    path = os.path.join(os.path.dirname(__file__), "..", "..", "db", "schema.sql")
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.connect() as conn:
        for stmt in sql.split(";"):
            s = stmt.strip()
            if not s:
                continue
            conn.execute(text(s))
        conn.commit()
