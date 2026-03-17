"""
CRUD operations for User and Transaction models.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Transaction, TransactionType, User

logger = logging.getLogger(__name__)


# ─── USER CRUD ────────────────────────────────────────────────────────────────

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
) -> User:
    """Get existing user or create a new one."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"New user created: {telegram_id}")

    return user


# ─── TRANSACTION CRUD ─────────────────────────────────────────────────────────

async def create_transaction(
    session: AsyncSession,
    user_id: int,
    amount: float,
    tx_type: TransactionType,
    category: str,
    description: Optional[str] = None,
) -> Transaction:
    """Create and persist a new transaction."""
    tx = Transaction(
        user_id=user_id,
        amount=amount,
        type=tx_type,
        category=category,
        description=description,
    )
    session.add(tx)
    await session.commit()
    await session.refresh(tx)
    return tx


async def get_transaction_by_id(
    session: AsyncSession, tx_id: int, user_id: int
) -> Optional[Transaction]:
    """Fetch a single transaction belonging to a user."""
    result = await session.execute(
        select(Transaction).where(
            Transaction.id == tx_id, Transaction.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def update_transaction(
    session: AsyncSession,
    tx_id: int,
    user_id: int,
    amount: Optional[float] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[Transaction]:
    """Update an existing transaction's fields."""
    tx = await get_transaction_by_id(session, tx_id, user_id)
    if tx is None:
        return None
    if amount is not None:
        tx.amount = amount
    if category is not None:
        tx.category = category
    if description is not None:
        tx.description = description
    await session.commit()
    await session.refresh(tx)
    return tx


async def delete_transaction(
    session: AsyncSession, tx_id: int, user_id: int
) -> bool:
    """Delete a transaction. Returns True if deleted, False if not found."""
    tx = await get_transaction_by_id(session, tx_id, user_id)
    if tx is None:
        return False
    await session.delete(tx)
    await session.commit()
    return True


async def get_recent_transactions(
    session: AsyncSession, user_id: int, limit: int = 10
) -> list[Transaction]:
    """Fetch the N most recent transactions for a user."""
    result = await session.execute(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_transactions_in_range(
    session: AsyncSession,
    user_id: int,
    start: datetime,
    end: datetime,
) -> list[Transaction]:
    """Fetch all transactions for a user within a date range."""
    result = await session.execute(
        select(Transaction).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.created_at >= start,
                Transaction.created_at <= end,
            )
        ).order_by(Transaction.created_at.desc())
    )
    return list(result.scalars().all())


async def get_balance(session: AsyncSession, user_id: int) -> dict[str, float]:
    """Calculate total income, expense and net balance for a user."""
    result = await session.execute(
        select(Transaction.type, func.sum(Transaction.amount))
        .where(Transaction.user_id == user_id)
        .group_by(Transaction.type)
    )
    rows = result.all()
    totals = {row[0]: row[1] for row in rows}
    income = totals.get(TransactionType.INCOME, 0.0)
    expense = totals.get(TransactionType.EXPENSE, 0.0)
    return {"income": income, "expense": expense, "balance": income - expense}


async def get_category_stats(
    session: AsyncSession,
    user_id: int,
    tx_type: TransactionType,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> list[tuple[str, float]]:
    """Get per-category totals for a user, optionally filtered by date range."""
    filters = [
        Transaction.user_id == user_id,
        Transaction.type == tx_type,
    ]
    if start:
        filters.append(Transaction.created_at >= start)
    if end:
        filters.append(Transaction.created_at <= end)

    result = await session.execute(
        select(Transaction.category, func.sum(Transaction.amount))
        .where(and_(*filters))
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
    )
    return list(result.all())
