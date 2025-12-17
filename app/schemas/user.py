from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.core.enums import UserRole


# Базовий клас (спільні поля)
class UserBase(BaseModel):
    username: str
    role: UserRole = UserRole.USER
    # role: str #old version without enum
    avatar: Optional[str] = None


# Схема для створення (POST) - пароль обов'язковий
class UserCreate(UserBase):
    # username: str
    # role: str
    password: str


# Схема для оновлення (PATCH) - всі поля опціональні
class UserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None # old version without enum
    # role: Optional[str] = None


# Схема для відповіді (GET) - повертаємо ID, але приховуємо пароль
class UserResponse(UserBase):
    id: int
    # username: str
    # # password_hash: str
    # role: str

    # Цей конфіг дозволяє Pydantic читати дані прямо з ORM-об'єктів SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
