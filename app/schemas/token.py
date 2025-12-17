from typing import Optional
from pydantic import BaseModel

# 1. Схема для ВІДПОВІДІ (те, що ми віддаємо клієнту після логіну)
class Token(BaseModel):
    access_token: str
    token_type: str

# 2. Схема для ПЕЙЛОАДУ (те, що зашито всередині токена)
# Це знадобиться нам пізніше, коли ми будемо розшифровувати токен,
# щоб переконатися, що там є username.
class TokenData(BaseModel):
    username: Optional[str] = None