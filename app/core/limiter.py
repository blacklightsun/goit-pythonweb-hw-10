from slowapi import Limiter
from slowapi.util import get_remote_address

# Ми використовуємо IP-адресу клієнта як ідентифікатор для обмеження
limiter = Limiter(key_func=get_remote_address)