"""
Finance service: business logic layer wrapping CRUD operations.
"""
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from database import crud
from database.models import Transaction, TransactionType, User

logger = logging.getLogger(__name__)


async def register_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str],
    full_name: Optional[str],
) -> User:
    """Ensure user exists in the database."""
    return await crud.get_or_create_user(session, telegram_id, username, full_name)


async def add_expense(
    session: AsyncSession,
    user_id: int,
    amount: float,
    category: str,
    description: Optional[str] = None,
) -> Transaction:
    """Record a new expense transaction."""
    tx = await crud.create_transaction(
        session,
        user_id=user_id,
        amount=amount,
        tx_type=TransactionType.EXPENSE,
        category=category,
        description=description,
    )
    logger.info(f"Expense added: user={user_id} amount={amount} cat={category}")
    return tx


async def add_income(
    session: AsyncSession,
    user_id: int,
    amount: float,
    category: str,
    description: Optional[str] = None,
) -> Transaction:
    """Record a new income transaction."""
    tx = await crud.create_transaction(
        session,
        user_id=user_id,
        amount=amount,
        tx_type=TransactionType.INCOME,
        category=category,
        description=description,
    )
    logger.info(f"Income added: user={user_id} amount={amount} cat={category}")
    return tx


async def get_balance_summary(
    session: AsyncSession, user_id: int
) -> dict[str, float]:
    """Return income/expense/balance totals for a user."""
    return await crud.get_balance(session, user_id)


async def get_recent(
    session: AsyncSession, user_id: int, limit: int = 10
) -> list[Transaction]:
    """Fetch most recent transactions."""
    return await crud.get_recent_transactions(session, user_id, limit)


async def edit_transaction(
    session: AsyncSession,
    tx_id: int,
    user_id: int,
    amount: Optional[float] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[Transaction]:
    """Edit an existing transaction."""
    return await crud.update_transaction(
        session, tx_id, user_id, amount, category, description
    )


async def remove_transaction(
    session: AsyncSession, tx_id: int, user_id: int
) -> bool:
    """Delete a transaction by ID."""
    return await crud.delete_transaction(session, tx_id, user_id)
