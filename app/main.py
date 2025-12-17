from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router  # Імпорт зібраного роутера
from app.core.config import settings

# Імпортуємо наш лімітер
from app.core.limiter import limiter

app = FastAPI(title=settings.PROJECT_NAME)

# --- НАЛАШТУВАННЯ CORS ---

# Список доменів, яким дозволено стукатись до вашого API.
# Для розробки зазвичай додають порти локалхоста, де живе фронтенд.
origins = [
    "http://localhost:3000", # React / Next.js
    "http://localhost:5173", # Vite (Vue / React)
    "http://localhost:8080", # Стандартний порт для багатьох фронтендів
    "http://127.0.0.1:3000",
    # "*"  # ⚠️ Можна використати "*", щоб дозволити всім, але це небезпечно для продакшену
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Яким доменам можна (список вище)
    allow_credentials=True,        # ⚠️ ВАЖЛИВО: Дозволяє передавати куки та Authorization хедери (JWT)
    allow_methods=["*"],           # Дозволяємо всі методи: GET, POST, PUT, DELETE, OPTIONS...
    allow_headers=["*"],           # Дозволяємо всі заголовки (Content-Type, Authorization...)
)

# --- ПІДКЛЮЧЕННЯ RATE LIMITER (те, що ми робили раніше) ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Підключення всіх роутів однією строкою
app.include_router(api_router, prefix="/api/v1")