import re
from datetime import datetime
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
    Boolean,
    Text
)
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy.sql import func

from src.database.database import Base


class BaseTable(Base):
    """AbstractModel"""

    __abstract__ = True
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:  # Set __tablename__ as Class name automatic
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

    def __str__(self):
        return f"<{self.__class__.__name__}({self.__dict__})>"

    def __repr__(self) -> str:
        return str(self)

    def as_dict(self) -> dict:
        """Response table as dict"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(BaseTable):
    """Table for registers users"""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True
    )
    participant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("participants.id", ondelete='CASCADE'),
        comment="Participant id",
    )
    is_santa: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )


class Participant(BaseTable):
    __tablename__ = "participants"

    name: Mapped[str] = mapped_column(
        String(64), unique=True
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    is_selected: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
