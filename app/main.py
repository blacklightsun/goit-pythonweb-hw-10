from fastapi import FastAPI
from app.api.v1 import api_router  # Імпорт зібраного роутера

# import appapi.v1 as api_v1
from app.core.config import settings

# print(dir(api_v1))
# print('===================')

app = FastAPI(title=settings.PROJECT_NAME)

# Підключення всіх роутів однією строкою
app.include_router(api_router, prefix="/api/v1")
