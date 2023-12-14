import datetime

from sqlalchemy import BigInteger, Boolean, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = "group"
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    autodelete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class GroupUser(Base):
    __tablename__ = "group_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger())
    group_id: Mapped[int] = mapped_column(BigInteger())
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger())
    name: Mapped[str] = mapped_column(String())
    username: Mapped[str] = mapped_column(String(), nullable=True)
    streak: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    attempts: Mapped[int]
    maximum_days: Mapped[int] = mapped_column(BigInteger())
    all_days: Mapped[int] = mapped_column(BigInteger())
