from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

from api import analitica, ingesta

app = FastAPI(title="SISC Jamundí API", version="0.1.0")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analitica.router, prefix="/analitica", tags=["analitica"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bienvenido al Sistema de Información para la Seguridad y la Convivencia (SISC) Jamundí"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(analitica.router, prefix="/analitica", tags=["analitica"])
app.include_router(ingesta.router, prefix="/ingesta", tags=["ingesta"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
