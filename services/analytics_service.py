"""
Analytics service: generates text-based financial reports.
"""
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from database import crud
from database.models import Transaction, TransactionType
from utils.helpers import (
    day_range,
    format_amount,
    month_range,
    progress_bar,
    truncate,
    week_range,
)

logger = logging.getLogger(__name__)


def _build_transaction_list(transactions: list[Transaction]) -> str:
    """Format a list of transactions into readable text."""
    if not transactions:
        return "  📭 Tranzaksiyalar topilmadi."
    lines = []
    for tx in transactions:
        emoji = "🔴" if tx.type == TransactionType.EXPENSE else "🟢"
        date_str = tx.created_at.strftime("%d.%m %H:%M")
        desc = f" — {truncate(tx.description)}" if tx.description else ""
        lines.append(
            f"  {emoji} #{tx.id} | {format_amount(tx.amount)} | "
            f"{tx.category}{desc} | {date_str}"
        )
    return "\n".join(lines)


def _build_category_breakdown(
    stats: list[tuple[str, float]], total: float, title: str
) -> str:
    """Format category statistics with progress bars."""
    if not stats:
        return f"  📭 {title} bo'yicha ma'lumot yo'q."
    lines = [f"  {title}:"]
    for category, amount in stats:
        bar = progress_bar(amount, total)
        lines.append(f"    {category}: {format_amount(amount)} {bar}")
    return "\n".join(lines)


async def daily_report(session: AsyncSession, user_id: int) -> str:
    """Generate today's financial summary."""
    start, end = day_range()
    transactions = await crud.get_transactions_in_range(session, user_id, start, end)

    income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
    expense = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)

    lines = [
        f"📅 *Bugungi hisobot* ({datetime.now().strftime('%d.%m.%Y')})\n",
        f"  🟢 Daromad:   {format_amount(income)}",
        f"  🔴 Xarajat:   {format_amount(expense)}",
        f"  💳 Saldo:      {format_amount(income - expense)}\n",
        f"📋 *Tranzaksiyalar:*",
        _build_transaction_list(transactions),
    ]
    return "\n".join(lines)


async def weekly_report(session: AsyncSession, user_id: int) -> str:
    """Generate this week's financial summary."""
    start, end = week_range()
    transactions = await crud.get_transactions_in_range(session, user_id, start, end)

    income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
    expense = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)

    lines = [
        f"📆 *Haftalik hisobot*\n",
        f"  🟢 Daromad:   {format_amount(income)}",
        f"  🔴 Xarajat:   {format_amount(expense)}",
        f"  💳 Saldo:      {format_amount(income - expense)}\n",
        f"📋 *Tranzaksiyalar ({len(transactions)} ta):*",
        _build_transaction_list(transactions[:15]),
    ]
    return "\n".join(lines)


async def monthly_report(session: AsyncSession, user_id: int) -> str:
    """Generate this month's financial summary with category breakdown."""
    start, end = month_range()
    transactions = await crud.get_transactions_in_range(session, user_id, start, end)

    income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
    expense = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)

    expense_stats = await crud.get_category_stats(
        session, user_id, TransactionType.EXPENSE, start, end
    )
    income_stats = await crud.get_category_stats(
        session, user_id, TransactionType.INCOME, start, end
    )

    month_name = datetime.now().strftime("%B %Y")
    lines = [
        f"🗓️ *{month_name} oylik hisobot*\n",
        f"  🟢 Jami daromad:  {format_amount(income)}",
        f"  🔴 Jami xarajat:  {format_amount(expense)}",
        f"  💳 Oylik saldo:   {format_amount(income - expense)}\n",
        _build_category_breakdown(expense_stats, expense, "🔴 Xarajat kategoriyalari"),
        "",
        _build_category_breakdown(income_stats, income, "🟢 Daromad kategoriyalari"),
    ]
    return "\n".join(lines)


async def category_stats_report(
    session: AsyncSession,
    user_id: int,
    tx_type: Optional[TransactionType] = None,
) -> str:
    """Generate an all-time category statistics report."""
    types_to_report = (
        [tx_type]
        if tx_type
        else [TransactionType.EXPENSE, TransactionType.INCOME]
    )
    sections = ["📊 *Kategoriyalar bo'yicha statistika*\n"]

    for t in types_to_report:
        stats = await crud.get_category_stats(session, user_id, t)
        total = sum(amt for _, amt in stats)
        label = "🔴 Xarajatlar" if t == TransactionType.EXPENSE else "🟢 Daromadlar"
        sections.append(_build_category_breakdown(stats, total, label))
        sections.append(f"  Jami: {format_amount(total)}\n")

    return "\n".join(sections)
