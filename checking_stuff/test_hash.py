# test_hash.py
from passlib.context import CryptContext

# Налаштування таке ж, як у вас
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    password = "user11"
    print(f"Testing hash for: {password}")
    
    hashed = pwd_context.hash(password)
    print(f"✅ Success! Hash: {hashed}")
    
    # Спробуємо довгий рядок для тесту
    long_pass = "a" * 73
    print(f"Testing long password ({len(long_pass)} chars)...")
    pwd_context.hash(long_pass)
    
except Exception as e:
    print(f"❌ Error caught: {e}")