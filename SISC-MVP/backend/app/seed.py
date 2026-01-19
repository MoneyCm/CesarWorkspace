from .db import SessionLocal
from .models import User
from .utils import hash_password

def create_admin():
    db = SessionLocal()
    user = db.query(User).filter(User.username == 'admin').first()
    if not user:
        u = User(username='admin', password_hash=hash_password('admin123'), role='admin')
        db.add(u)
        db.commit()
        print('Admin user created: admin / admin123')
    else:
        print('Admin already exists')
