from sqlalchemy import ForeignKey, Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

# from app.models.user import User
from datetime import date


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firstname: Mapped[str] = mapped_column(String(50))
    lastname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True)
    birthday: Mapped[date] = mapped_column(Date)  # Format: YYYY-MM-DD
    other_details: Mapped[str] = mapped_column(String(250))
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )  # ForeignKey can be added when User model is uncommented

    owner: Mapped[str] = relationship("User", back_populates="contacts")

    def __repr__(self) -> str:
        return (
            f"Contact(id={self.id!r}, firstname={self.firstname!r}, "
            f"lastname={self.lastname!r}, email={self.email!r}, "
            f"phone_number={self.phone_number!r}, birthday={self.birthday!r}, "
            f"other_details={self.other_details!r}), owner_id={self.owner_id!r})"
        )
