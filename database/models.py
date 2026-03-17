"""
Database models for Finance Tracker Bot.
"""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class TransactionType(str, PyEnum):
    """Transaction type enumeration."""
    INCOME = "income"
    EXPENSE = "expense"


class Category(str, PyEnum):
    """Expense/income category enumeration."""
    # Expense categories
    FOOD = "🍔 Ovqat"
    TRANSPORT = "🚗 Transport"
    BILLS = "💡 Kommunal"
    SHOPPING = "🛍️ Xarid"
    HEALTH = "💊 Salomatlik"
    ENTERTAINMENT = "🎭 Ko'ngil ochar"
    EDUCATION = "📚 Ta'lim"
    OTHER = "📦 Boshqa"
    # Income categories
    SALARY = "💼 Maosh"
    FREELANCE = "💻 Freelance"
    BUSINESS = "🏪 Biznes"
    INVESTMENT = "📈 Investitsiya"
    GIFT = "🎁 Sovg'a"
    OTHER_INCOME = "💰 Boshqa daromad"


EXPENSE_CATEGORIES = [
    Category.FOOD,
    Category.TRANSPORT,
    Category.BILLS,
    Category.SHOPPING,
    Category.HEALTH,
    Category.ENTERTAINMENT,
    Category.EDUCATION,
    Category.OTHER,
]

INCOME_CATEGORIES = [
    Category.SALARY,
    Category.FREELANCE,
    Category.BUSINESS,
    Category.INVESTMENT,
    Category.GIFT,
    Category.OTHER_INCOME,
]


class User(Base):
    """Telegram user model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User telegram_id={self.telegram_id}>"


class Transaction(Base):
    """Financial transaction model."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType), nullable=False
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} type={self.type} amount={self.amount}>"
