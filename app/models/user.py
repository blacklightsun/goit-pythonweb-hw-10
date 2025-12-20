from sqlalchemy import Integer, String, Boolean, Enum, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.core.enums import UserRole
# from app.models.contact import Contact


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Використовуємо наш Enum як тип колонки
    # default=UserRole.USER означає, що якщо роль не вказана, це буде звичайний юзер
    role: Mapped[UserRole] = mapped_column(Enum(
        UserRole, 
        name="userrole",  # Назва типу в Postgres (має збігатися з міграцією!)
        create_type=False, # Тип вже створений міграцією, не намагайся створити знову
        values_callable=lambda obj: [e.value for e in obj]
        ), default=UserRole.USER)
    # role: Mapped[str] = mapped_column(String(20)) #old version without enum
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact", back_populates="owner", cascade="all, delete-orphan"
    )
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, role={self.role!r}, avatar={self.avatar!r})"