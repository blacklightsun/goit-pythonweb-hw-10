from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# Створення двигуна (Engine)
# echo=True виводитиме SQL-запити в консоль (корисно для дебагу)
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Створення фабрики сесій
# Ми будемо використовувати цей клас для створення сесії в кожному запиті
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    # autoflush=False,
    expire_on_commit=False,
)
