from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.db.deps import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.models.user import User
from app.crud.crud_users import get_user_by_username, get_user_by_email, create_user, confirmed_email
from app.services.auth import create_access_token, verify_password, get_email_from_token
from app.services.verify_email import send_verifying_email

router = APIRouter()

# --- LOGIN ---
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    # 1. Знаходимо юзера в БД
    db_user = await get_user_by_username(db, form_data.username)

    # 2. Перевіряємо: чи юзер існує І чи правильний пароль
    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not db_user.confirmed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Електронна адреса не підтверджена",
            )


    # 3. Генеруємо токен
    # У поле "sub" (subject) зазвичай кладуть унікальний ідентифікатор (username або email)
    access_token = create_access_token(data={"sub": db_user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}

# --- REGISTER NEW USER ---
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    email_user = await get_user_by_email(db, user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await get_user_by_username(db, user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    
    new_user = await create_user(db, user_data)
    background_tasks.add_task(
        send_verifying_email, new_user.email, new_user.username, str(request.base_url)
    )
    return new_user

# --- VERIFY EMAIL ---
@router.get("/verify-email/{username}/{token}", status_code=status.HTTP_200_OK)
async def verify_email(
    username: str, 
    token: str, 
    db: AsyncSession = Depends(get_db)
    ):
    # print(f"DEBUG: Verifying email for user: {username} with token: {token}")
    user: User = await get_user_by_username(db, username)
    email: str = await get_email_from_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача не знайдено",
        )
    
    if user.confirmed:
        return {"message": "Електронна адреса вже підтверджена."}

    if user.email != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невірний токен підтвердження.",
        )
    
    await confirmed_email(db,  user)
    return {"message": "Електронна адреса успішно підтверджена."}