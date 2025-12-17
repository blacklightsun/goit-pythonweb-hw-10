from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db import deps
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.crud import crud_contacts
from app.services.auth import get_current_user
from app.models.user import User

# Оголошення
router = APIRouter()


# 7. GET (Read All birthdaays in next n days)
@router.get("/birthdays", response_model=List[ContactResponse])
async def read_contacts_for_birthdays(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    days_ahead: int = 7,
    skip: int = 0,
    limit: int = 10,
    ):

    contacts = await crud_contacts.get_contacts_by_birthdays(
        db, days_ahead=days_ahead, skip=skip, limit=limit, user=current_user
    )
    return contacts


# 1. GET (Read All with optional search query parameter)
@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    query: str | None = None,  # Зробіть query опціональним
    skip: int = 0,
    limit: int = 10,
    ):
    if query:
        # Якщо query передано - шукаємо
        return await crud_contacts.get_contacts_by_query(
            db, query=query, skip=skip, limit=limit, user=current_user
        )

    # Якщо query немає - повертаємо всі
    return await crud_contacts.get_contacts(db, skip=skip, limit=limit, user=current_user)



# 2. POST (Create)
@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_in: ContactCreate, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    # Тут можна додати перевірку, чи існує вже такий email
    new_contact = await crud_contacts.create_contact(db, contact_in, user=current_user)
    if not new_contact:
        raise HTTPException(
            status_code=400,
            detail="Contact with this email or phone number already exists",
        )
    return new_contact


# 3. GET (Read One)
@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(deps.get_db),
    ):

    contact = await crud_contacts.get_contact(db=db, contact_id=contact_id, user=current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


# 4. PATCH (Update) - використовуємо PATCH для часткового оновлення
@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    contact = await crud_contacts.update_contact(db=db, contact_id=contact_id, contact_update=contact_update, user=current_user)
    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found or contact with this email or phone number already exists",
        )
    return contact


# 5. DELETE
@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, 
                         db: AsyncSession = Depends(deps.get_db),
                         current_user: User = Depends(get_current_user),
                         ):
    contact = await crud_contacts.delete_contact(db=db, contact_id=contact_id, user=current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return None
