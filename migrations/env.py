import asyncio
from logging.config import fileConfig
import os
import sys

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.db.base import Base  # імпортуємо Base з нашого додатку

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
# Це об'єкт конфігурації Alembic, що дає доступ до значень з .ini файлу
config = context.config

# --- 1. ДОДАВАННЯ ШЛЯХУ ДО ПРОЄКТУ ---
# Alembic запускається з кореня, але йому треба бачити папку app/
# Без цього рядка буде помилка: ModuleNotFoundError: No module named 'app'
sys.path.append(os.getcwd())

# --- 2. ІМПОРТ НАЛАШТУВАНЬ ТА МОДЕЛЕЙ ---
# Імпортуємо наш конфіг, щоб взяти URL бази даних
from app.core.config import settings

# Імпортуємо Base саме з файлу-агрегатора (де зібрані всі моделі)
from app.db.base import Base

# --- 3. ПЕРЕВИЗНАЧЕННЯ URL БАЗИ ДАНИХ ---
# Ми не хочемо хардкодити пароль в alembic.ini.
# Ми беремо URL з нашого settings (який читає .env)
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))


# Interpret the config file for Python logging.
# This line sets up loggers basically.
# Налаштування логування
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# --- 4. ПРИВ'ЯЗКА МЕТАДАНИХ ---
# Це найважливіше. Alembic порівнює цю змінну з реальною БД
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# --- 5. РЕЖИМ OFFLINE (Генерація SQL скриптів без підключення) ---
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# --- 6. ДОПОМІЖНА ФУНКЦІЯ ДЛЯ СИНХРОННОГО ЗАПУСКУ ---
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


# --- 7. РЕЖИМ ONLINE (Реальне застосування міграцій) ---
async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Створюємо асинхронний engine на основі конфігу
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        # Alembic всередині синхронний, тому ми запускаємо його через run_sync
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
