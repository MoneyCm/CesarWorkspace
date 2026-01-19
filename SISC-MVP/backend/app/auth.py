from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from .db import SessionLocal
from .models import User
from .utils import verify_password, hash_password, create_access_token, decode_token

router = APIRouter()
security = HTTPBearer()


@router.post('/auth/login')
def login(form: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail='Invalid token')
    db = SessionLocal()
    user = db.query(User).filter(User.username == payload.get('sub')).first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user


def require_role(role: str):
    def _inner(user: User = Depends(get_current_user)):
        if user.role != role and user.role != 'admin':
            raise HTTPException(status_code=403, detail='Insufficient privileges')
        return user
    return _inner
