from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

from api import analitica, ingesta, auth, reportes

app = FastAPI(title="SISC Jamundí API", version="0.1.0")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Cambiado a False para permitir "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SISC Jamundí API is running"}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(analitica.router, prefix="/analitica", tags=["analitica"])
app.include_router(ingesta.router, prefix="/ingesta", tags=["ingesta"])
app.include_router(reportes.router, prefix="/reportes", tags=["reportes"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
