from fastapi import HTTPException, Cookie
from jose import jwt
from database import Session
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'

def get_repo():
    session = Session()
    try:
        yield session
    finally:
        session.close()
        
def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Вы не авторизованы")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": int(payload["sub"]), "role": payload["role"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Сессия истекла")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")