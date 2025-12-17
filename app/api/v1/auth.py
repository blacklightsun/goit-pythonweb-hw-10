from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.models.user import User
from app.services.auth import create_access_token, verify_password
from app.schemas.token import Token # Створіть просту схему {access_token: str, token_type: str}

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # 1. Знаходимо юзера в БД
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    # 2. Перевіряємо: чи юзер існує І чи правильний пароль
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Генеруємо токен
    # У поле "sub" (subject) зазвичай кладуть унікальний ідентифікатор (username або email)
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}