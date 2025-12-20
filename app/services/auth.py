# app/services/auth.py
from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.user import User
from app.core.config import settings

# НАЛАШТУВАННЯ (в реальному проекті це має бути в .env файлі!)
JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM 
JWT_EXPIRATION_SECONDS = settings.JWT_EXPIRATION_SECONDS

# Налаштування контексту для хешування паролів (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема OAuth2: вказуємо, де знаходиться ендпоінт для отримання токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# --- ФУНКЦІЇ ХЕШУВАННЯ ---

def verify_password(plain_password, hashed_password):
    """Перевіряє, чи співпадає звичайний пароль з хешем"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Генерує хеш з пароля"""
    return pwd_context.hash(password)

# --- ФУНКЦІЇ ТОКЕНІВ ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Створює JWT токен з даними (payload)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(seconds=JWT_EXPIRATION_SECONDS)
    
    # Додаємо час закінчення життя токена
    to_encode.update({"exp": expire})
    
    # Кодуємо токен
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_email_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


# --- ГОЛОВНА ЗАЛЕЖНІСТЬ (DEPENDENCY) ---

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Ця функція буде 'охоронцем'. Вона:
    1. Прийме токен з заголовка запиту.
    2. Розшифрує його.
    3. Знайде користувача в БД.
    4. Поверне об'єкт User або помилку 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Розкодовуємо токен
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Шукаємо юзера в базі (тут треба адаптувати під ваш код, якщо він асинхронний)
    # Припускаємо, що у вас є метод для пошуку по імені
    # Для асинхронного SQLAlchemy:
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    
    return user

async def get_email_from_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )