# app/db/base_class.py
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Базовий клас для всіх моделей.
    """

    # Автоматична генерація __tablename__
    # Якщо ви не вкажете назву таблиці вручну, вона буде взята з назви класу (у нижньому регістрі)
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
