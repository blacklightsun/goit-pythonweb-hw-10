import enum


# Створюємо клас-перерахування
# Ми успадковуємо від str, щоб Pydantic/JSON розуміли це як рядок "admin", а не як складний об'єкт
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"