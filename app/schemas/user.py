from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.core.enums import UserRole


# Базовий клас (спільні поля)
class UserBase(BaseModel):
    username: str
    role: UserRole = UserRole.USER
    avatar: Optional[str] = None
    email: str
    # confirmed: Optional[bool] = False


# Схема для створення (POST) - пароль обов'язковий
class UserCreate(UserBase):
    password: str


# Схема для оновлення (PATCH) - всі поля опціональні
class UserUpdate(BaseModel):
    # username: Optional[str] = None
    role: Optional[UserRole] = None # old version without enum
    email: Optional[str] = None
    avatar: Optional[str] = None
    # confirmed: Optional[bool] = False


# Схема для відповіді (GET) - повертаємо ID, але приховуємо пароль
class UserResponse(UserBase):
    id: int

    # Цей конфіг дозволяє Pydantic читати дані прямо з ORM-об'єктів SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
