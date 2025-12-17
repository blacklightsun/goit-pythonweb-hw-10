from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api import deps
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.crud import crud_users
from app.models.user import User
from app.services.auth import get_current_user
from app.core.limiter import limiter  # Імпорт лімітеру з main.py

router = APIRouter()

# Endpoint для отримання інформації про поточного користувача з лімітом запитів
@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")  # 👈 ОБМЕЖЕННЯ: 5 запитів на хвилину
async def read_users_me(
    request: Request, # 👈 ОБОВ'ЯЗКОВО для роботи лімітера!
    current_user: User = Depends(get_current_user)
):
    """
    Повертає профіль поточного користувача.
    Ліміт: 5 запитів на хвилину.
    """
    return current_user

# 1. GET (Read All)
@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(deps.get_db)
):
    users = await crud_users.get_users(db, skip=skip, limit=limit)
    return users


# 2. POST (Create)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(deps.get_db)):
    # Тут можна додати перевірку, чи існує вже такий email
    user = await crud_users.create_user(db, user_in)
    if not user:
        raise HTTPException(status_code=409, detail="User already exists")
    return user


# 3. GET (Read One)
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(deps.get_db)):
    user = await crud_users.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 4. PATCH (Update) - використовуємо PATCH для часткового оновлення
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(deps.get_db)
):
    user = await crud_users.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 5. DELETE
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(deps.get_db)):
    user = await crud_users.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return None
