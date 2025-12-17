from fastapi import APIRouter
from app.api.v1 import users, contacts


api_router = APIRouter()

# Підключаємо роутери до основного роутера API
# tags=["..."] додає красиві заголовки в Swagger UI
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
