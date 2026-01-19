import os
import time
from fastapi import FastAPI
from . import db
from .api import router as api_router
from . import seed

app = FastAPI(title="SISC-MVP")

@app.on_event("startup")
def startup():
    # wait for DB
    db_url = os.getenv("DATABASE_URL")
    for _ in range(20):
        try:
            db.init_db()
            break
        except Exception:
            time.sleep(1)
    try:
        seed.create_admin()
    except Exception:
        pass

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
