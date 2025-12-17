from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from typing import Optional


class ContactCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    phone_number: str
    birthday: date
    other_details: str
    owner_id: int


class ContactUpdate(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    birthday: Optional[date] = None
    other_details: str | None = None
    # owner_id: int | None = None # Usually we don't update owner_id


class ContactResponse(ContactCreate):
    id: int

    # Цей конфіг дозволяє Pydantic читати дані прямо з ORM-об'єктів SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
