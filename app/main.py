from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router  # Імпорт зібраного роутера
from app.core.config import settings
from app.core.limiter import limiter



app = FastAPI(title=settings.PROJECT_NAME)

# --- НАЛАШТУВАННЯ CORS ---
app.add_middleware(
    CORSMiddleware,
    # 👇 Перетворюємо URL-об'єкти назад у рядки
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for origin in settings.BACKEND_CORS_ORIGINS:
    print(f"CORS origin allowed: {origin}")


# --- ПІДКЛЮЧЕННЯ RATE LIMITER (те, що ми робили раніше) ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Підключення всіх роутів однією строкою
app.include_router(api_router, prefix="/api/v1")


