from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth import get_password_hash


# --- READ (Get All) ---
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    # select(User) створює запит SELECT * FROM users
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


# --- CREATE ---
async def create_user(db: AsyncSession, user_in: UserCreate):
    # Створюємо об'єкт моделі
    # 👇 ДОДАЙТЕ ЦЕЙ БЛОК ДЛЯ ПЕРЕВІРКИ 👇
    print(f"DEBUG: Type of password: {type(user_in.password)}")
    print(f"DEBUG: Password length: {len(user_in.password)}")
    print(f"DEBUG: Password content: {user_in.password}")
    # 👆 ------------------------------- 👆
    hashed_password = get_password_hash(user_in.password)

    db_user = await get_user_by_username(db, user_in.username)
    if db_user:
        return None
    
    db_user = await get_user_by_email(db, user_in.email)
    if db_user:
        return None

    db_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_password, 
        role=user_in.role,
        avatar=user_in.avatar,
    )
    db.add(db_user)
    await db.commit()  # Зберігаємо в БД
    await db.refresh(db_user)  # Оновлюємо об'єкт (отримуємо ID, який видала база)
    return db_user


# --- READ (Get By ID) ---
async def get_user(db: AsyncSession, user_id: int):
    # session.get - найшвидший спосіб отримати по Primary Key
    return await db.get(User, user_id)


# --- UPDATE ---
async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate):

    # Перевірка унікальності email, якщо він оновлюється
    if user_update.email:
        db_user = await get_user_by_email(db, user_update.email)
        if db_user and db_user.id != user_id:
            return None
        
    # Спочатку знаходимо об'єкт
    db_user = await get_user(db, user_id)
    if not db_user:
        return None
    
    # Оновлюємо тільки ті поля, які прийшли (exclude_unset=True)
    update_data = user_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        print(f"DEBUG: Updating {key} to {value}")  # Додатковий лог
        setattr(db_user, key, value)  # Оновлюємо атрибути об'єкта

    await db.commit()
    await db.refresh(db_user)
    return db_user


# --- DELETE ---
async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    await db.delete(db_user)
    await db.commit()
    return db_user


# --- GET USER BY USERNAME ---
async def get_user_by_username(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalars().first()


# --- GET USER BY EMAIL ---
async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalars().first()

# # --- AUTHENTICATE USER ---
# async def authenticate_user(db: AsyncSession, username: str, password: str):
#     stmt = select(User).where(User.username == username)
#     result = await db.execute(stmt)
#     user = result.scalars().first()
#     if user and user.password_hash == password + '_hashed':  # Тимчасова перевірка
#         return user
#     return None


# # --- CHANGE USER ROLE ---
# async def change_user_role(db: AsyncSession, user_id: int, new_role: str):
#     db_user = await get_user(db, user_id)
#     if not db_user:
#         return None

#     db_user.role = new_role
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user

# # --- GET USERS BY ROLE ---
# async def get_users_by_role(db: AsyncSession, role: str, skip: int = 0, limit: int = 10):
#     stmt = select(User).where(User.role == role).offset(skip).limit(limit)
#     result = await db.execute(stmt)
#     return result.scalars().all()

# # --- RESET USER PASSWORD ---
# async def reset_user_password(db: AsyncSession, user_id: int, new_password: str):
#     db_user = await get_user(db, user_id)
#     if not db_user:
#         return None

#     db_user.hashed_password = new_password + '_hashed'  # Тимчасове хешування
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user

# # --- GET TOTAL USER COUNT ---
# async def get_total_user_count(db: AsyncSession):
#     stmt = select(User)
#     result = await db.execute(stmt)
#     return result.scalars().count()

# # --- GET USERS WITH PAGINATION AND ROLE FILTER ---
# async def get_users_with_pagination_and_role(
#     db: AsyncSession, role: str, skip: int = 0, limit: int = 10
# ):
#     stmt = select(User).where(User.role == role).offset(skip).limit(limit)
#     result = await db.execute(stmt)
#     return result.scalars().all()
