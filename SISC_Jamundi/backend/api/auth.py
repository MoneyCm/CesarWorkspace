from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from core.security import verify_password, create_access_token, get_password_hash
# Nota: Aquí se integrarían los modelos de DB en el siguiente paso

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Mock de validación para el primer levantado del sistema
    # En el siguiente paso usaremos la DB real
    if form_data.username == "admin" and form_data.password == "admin123":
        access_token = create_access_token(data={"sub": form_data.username, "role": "Admin SISC"})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuario o contraseña incorrectos",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Lógica para decodificar token y devolver info del usuario
    return {"username": "admin", "role": "Admin SISC"}
