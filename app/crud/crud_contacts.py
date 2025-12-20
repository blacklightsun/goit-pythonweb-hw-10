# from ast import stmt
from datetime import date, timedelta
from sqlalchemy import select, func, cast, Integer, case, bindparam

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactUpdate


# --- READ (Get All) ---
async def get_contacts(db: AsyncSession, user: User, skip: int = 0, limit: int = 10):
    stmt = select(Contact).where(Contact.owner_id == user.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


# --- CREATE ---
async def create_contact(db: AsyncSession, contact_in: ContactCreate, user: User):
    """Створює новий контакт у базі даних"""
    if await check_contact_email_exists_for_creating(db, contact_in.email, user):
        return None

    if await check_contact_phone_exists_for_creating(db, contact_in.phone_number, user):
        return None

    # Створюємо об'єкт моделі
    # Тут треба хешувати пароль, але для спрощення поки пишемо plain text
    db_contact = Contact(
        firstname=contact_in.firstname,
        lastname=contact_in.lastname,
        email=contact_in.email,
        phone_number=contact_in.phone_number,
        birthday=contact_in.birthday,
        other_details=contact_in.other_details,
        owner_id=user.id,
    )
    db.add(db_contact)
    await db.commit()  # Зберігаємо в БД
    await db.refresh(db_contact)  # Оновлюємо об'єкт (отримуємо ID, який видала база)
    return db_contact


# --- READ (Get By ID) ---
async def get_contact(db: AsyncSession, contact_id: int, user: User):
    stmt = select(Contact).where(Contact.id == contact_id, Contact.owner_id == user.id)
    result = await db.execute(stmt)
    return result.scalars().first()


# --- UPDATE ---
async def update_contact(
    db: AsyncSession, contact_id: int, contact_update: ContactUpdate, user: User
):
    # Спочатку знаходимо об'єкт
    db_contact = await get_contact(db, contact_id, user)
    if not db_contact:
        return None

    if contact_update.email:
        if await check_contact_email_exists_for_updating(db, contact_update.email, contact_id, user):
            return None

    if contact_update.phone_number:
        if await check_contact_phone_exists_for_updating(db, contact_update.phone_number, contact_id, user):
            return None

    # Оновлюємо тільки ті поля, які прийшли (exclude_unset=True)
    update_data = contact_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_contact, key, value)  # Оновлюємо атрибути об'єкта

    await db.commit()
    await db.refresh(db_contact)
    return db_contact


# --- DELETE ---
async def delete_contact(db: AsyncSession, contact_id: int, user: User):
    db_contact = await get_contact(db, contact_id, user)
    if not db_contact:
        return None

    await db.delete(db_contact)
    await db.commit()
    return db_contact


# --- READ (Get All by query) ---
async def get_contacts_by_query(
    db: AsyncSession, query: str, user: User, skip: int = 0, limit: int = 10
):
    stmt = (
        select(Contact)
        .where(Contact.owner_id == user.id)  # Фільтр за власником, якщо потрібно
        .where(
            (Contact.firstname.ilike(f"%{query}%"))
            | (Contact.lastname.ilike(f"%{query}%"))
            | (Contact.email.ilike(f"%{query}%"))
            | (Contact.phone_number.ilike(f"%{query}%"))
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()



async def get_contacts_by_birthdays(
        db: AsyncSession, 
        user: User,
        days_ahead: int = 7, 
        skip: int = 0, 
        limit: int = 100
        ):
    today = date.today()
    end_date = today + timedelta(days=days_ahead)

    month_expr = cast(func.extract("month", Contact.birthday), Integer)
    day_expr = cast(func.extract("day", Contact.birthday), Integer)
    current_year_expr = cast(func.extract("year", func.current_date()), Integer)

    birthday_this_year = func.make_date(current_year_expr, month_expr, day_expr)

    next_birthday = case(
        (
            birthday_this_year < func.current_date(),
            func.make_date(current_year_expr + 1, month_expr, day_expr),
        ),
        else_=birthday_this_year,
    ).label("next_birthday")

    stmt = (
        select(Contact)
        .where(Contact.owner_id == user.id)
        .where(next_birthday.between(func.current_date(), bindparam("end_date")))
        .order_by(next_birthday)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt.params(end_date=end_date))
    return result.scalars().all()


async def check_contact_email_exists_for_creating(db: AsyncSession, email: str | None, user: User) -> bool:
    stmt = select(Contact) \
    .where(Contact.owner_id == user.id) \
    .where(Contact.email == email)
    result = await db.execute(stmt)
    contact = result.scalars().first()
    return contact is not None


async def check_contact_phone_exists_for_creating(db: AsyncSession, phone: str | None, user: User) -> bool:
    stmt = select(Contact) \
    .where(Contact.owner_id == user.id) \
    .where(Contact.phone_number == phone,)
    result = await db.execute(stmt)
    contact = result.scalars().first()
    return contact is not None

async def check_contact_email_exists_for_updating(db: AsyncSession, email: str | None, contact_id: int, user: User) -> bool:
    stmt = select(Contact) \
    .where(Contact.owner_id == user.id) \
    .where(Contact.email == email, Contact.id != contact_id,)
    result = await db.execute(stmt)
    contact = result.scalars().first()
    return contact is not None


async def check_contact_phone_exists_for_updating(db: AsyncSession, phone: str | None, contact_id: int, user: User) -> bool:
    stmt = select(Contact) \
    .where(Contact.owner_id == user.id) \
    .where(Contact.phone_number == phone, Contact.id != contact_id,)
    result = await db.execute(stmt)
    contact = result.scalars().first()
    return contact is not None
