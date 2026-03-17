"""
Handlers for financial reports and balance display.
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from database.db import AsyncSessionLocal
from keyboards.reply import main_menu_keyboard, report_menu_keyboard
from services.analytics_service import (
    category_stats_report,
    daily_report,
    monthly_report,
    weekly_report,
)
from services.finance_service import get_balance_summary, get_recent, register_user
from utils.helpers import format_amount

router = Router()
logger = logging.getLogger(__name__)


async def _get_user_id(session, from_user) -> int:
    user = await register_user(
        session, from_user.id, from_user.username, from_user.full_name
    )
    return user.id


# ─── BALANCE ──────────────────────────────────────────────────────────────────

@router.message(F.text == "💳 Balans")
@router.message(Command("balance"))
async def show_balance(message: Message) -> None:
    """Show current balance summary."""
    async with AsyncSessionLocal() as session:
        user_id = await _get_user_id(session, message.from_user)
        summary = await get_balance_summary(session, user_id)

    balance = summary["balance"]
    balance_emoji = "🟢" if balance >= 0 else "🔴"

    await message.answer(
        "💳 *Joriy balans*\n\n"
        f"  🟢 Jami daromad:  {format_amount(summary['income'])}\n"
        f"  🔴 Jami xarajat:  {format_amount(summary['expense'])}\n"
        f"  {balance_emoji} Sof saldo:     {format_amount(balance)}",
        parse_mode="Markdown",
        reply_markup=main_menu_inline_keyboard(),
    )


# ─── RECENT TRANSACTIONS ──────────────────────────────────────────────────────

@router.message(F.text == "📋 So'nggi tranzaksiyalar")
async def show_recent(message: Message) -> None:
    """Show last 10 transactions."""
    async with AsyncSessionLocal() as session:
        user_id = await _get_user_id(session, message.from_user)
        transactions = await get_recent(session, user_id, limit=10)

    if not transactions:
        await message.answer(
            "📭 Hozircha tranzaksiyalar yo'q.\n\n"
            "➕ Xarajat yoki daromad qo'shing!",
            reply_markup=main_menu_inline_keyboard(),
        )
        return

    lines = ["📋 *So'nggi 10 ta tranzaksiya*\n"]
    for tx in transactions:
        emoji = "🔴" if tx.type.value == "expense" else "🟢"
        date_str = tx.created_at.strftime("%d.%m.%Y %H:%M")
        desc = f"\n      📝 {tx.description}" if tx.description else ""
        lines.append(
            f"{emoji} *#{tx.id}* | {format_amount(tx.amount)}\n"
            f"      🏷️ {tx.category} | {date_str}{desc}\n"
        )

    await message.answer(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=main_menu_inline_keyboard(),
    )


# ─── REPORT MENU ──────────────────────────────────────────────────────────────

@router.message(F.text == "📊 Hisobot")
@router.message(Command("report"))
async def show_report_menu(message: Message) -> None:
    """Show report sub-menu."""
    await message.answer(
        "📊 *Hisobot turi ni tanlang:*",
        parse_mode="Markdown",
        reply_markup=report_menu_keyboard(),
    )


@router.message(F.text == "🔙 Orqaga")
async def back_to_main(message: Message) -> None:
    """Return to main menu."""
    await message.answer(
        "🏠 Asosiy menyu",
        reply_markup=main_menu_inline_keyboard()    )


# ─── REPORT TYPES ─────────────────────────────────────────────────────────────

@router.message(F.text == "📅 Bugungi hisobot")
async def report_daily(message: Message) -> None:
    """Show today's report."""
    async with AsyncSessionLocal() as session:
        user_id = await _get_user_id(session, message.from_user)
        report = await daily_report(session, user_id)

    await message.answer(report, parse_mode="Markdown", reply_markup=report_menu_keyboard())


@router.message(F.text == "📆 Haftalik hisobot")
async def report_weekly(message: Message) -> None:
    """Show this week's report."""
    async with AsyncSessionLocal() as session:
        user_id = await _get_user_id(session, message.from_user)
        report = await weekly_report(session, user_id)

    await message.answer(report, parse_mode="Markdown", reply_markup=report_menu_keyboard())


@router.message(F.text == "🗓️ Oylik hisobot")
async def report_monthly(message: Message) -> None:
    """Show this month's report."""
    async with AsyncSessionLocal() as session:
        user_id = await _get_user_id(session, message.from_user)
        report = await monthly_report(session, user_id)

    await message.answer(report, parse_mode="Markdown", reply_markup=report_menu_keyboard())


@router.message(F.text == "📈 Kategoriyalar bo'yicha")
async def report_categories(message: Message) -> None:
    """Show all-time category statistics."""
    async with AsyncSessionLocal() as session:
        user_id = await _get_user_id(session, message.from_user)
        report = await category_stats_report(session, user_id)

    await message.answer(report, parse_mode="Markdown", reply_markup=report_menu_keyboard())
