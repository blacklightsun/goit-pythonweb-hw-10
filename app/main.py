from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi import FastAPI, Request

from app.api.v1 import api_router  # Імпорт зібраного роутера
from app.core.config import settings

# Імпортуємо наш лімітер
from app.core.limiter import limiter

app = FastAPI(title=settings.PROJECT_NAME)

# 👇 1. Підключаємо лімітер до стану додатка
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Підключення всіх роутів однією строкою
app.include_router(api_router, prefix="/api/v1")