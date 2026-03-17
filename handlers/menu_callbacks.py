"""
Central hub for main menu callback queries.
Routes nav: and menu: callbacks to the correct action.
"""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline import (
    back_to_menu_keyboard,
    main_menu_keyboard,
    reports_keyboard,
)
from services.finance_service import get_balance_summary, get_recent, register_user
from services.analytics_service import (
    daily_report, weekly_report, monthly_report, category_stats_report,
)
from database.db import AsyncSessionLocal
from utils.helpers import format_amount

router = Router()
logger = logging.getLogger(__name__)


async def _get_user(session, from_user):
    return await register_user(
        session, from_user.id, from_user.username, from_user.full_name
    )


# ─── NAV: MAIN MENU ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "nav:main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "🏠 *Asosiy menyu*\nQuyidagi bo'limdan birini tanlang 👇",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


# ─── NAV: CANCEL ─────────────────────────────────────────────────────────────

@router.callback_query(F.data == "nav:cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "❌ *Bekor qilindi.*\n\nAsosiy menyu 👇",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


# ─── MENU: BALANCE ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:balance")
async def cb_balance(callback: CallbackQuery) -> None:
    async with AsyncSessionLocal() as session:
        user = await _get_user(session, callback.from_user)
        summary = await get_balance_summary(session, user.id)
    balance = summary["balance"]
    emoji = "🟢" if balance >= 0 else "🔴"
    await callback.message.edit_text(
        "💳 *Joriy balans*\n\n"
        f"  🟢 Daromad:  {format_amount(summary['income'])}\n"
        f"  🔴 Xarajat:  {format_amount(summary['expense'])}\n"
        f"  {emoji} Saldo:    {format_amount(balance)}",
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


# ─── MENU: REPORTS ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:reports")
async def cb_reports_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "📊 *Hisobot turini tanlang:*",
        parse_mode="Markdown",
        reply_markup=reports_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "report:daily")
async def cb_report_daily(callback: CallbackQuery) -> None:
    async with AsyncSessionLocal() as session:
        user = await _get_user(session, callback.from_user)
        report = await daily_report(session, user.id)
    await callback.message.edit_text(
        report, parse_mode="Markdown", reply_markup=reports_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "report:weekly")
async def cb_report_weekly(callback: CallbackQuery) -> None:
    async with AsyncSessionLocal() as session:
        user = await _get_user(session, callback.from_user)
        report = await weekly_report(session, user.id)
    await callback.message.edit_text(
        report, parse_mode="Markdown", reply_markup=reports_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "report:monthly")
async def cb_report_monthly(callback: CallbackQuery) -> None:
    async with AsyncSessionLocal() as session:
        user = await _get_user(session, callback.from_user)
        report = await monthly_report(session, user.id)
    await callback.message.edit_text(
        report, parse_mode="Markdown", reply_markup=reports_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "report:categories")
async def cb_report_categories(callback: CallbackQuery) -> None:
    async with AsyncSessionLocal() as session:
        user = await _get_user(session, callback.from_user)
        report = await category_stats_report(session, user.id)
    await callback.message.edit_text(
        report, parse_mode="Markdown", reply_markup=reports_keyboard()
    )
    await callback.answer()


# ─── MENU: RECENT TRANSACTIONS ────────────────────────────────────────────────

@router.callback_query(F.data == "menu:recent")
async def cb_recent(callback: CallbackQuery) -> None:
    from keyboards.inline import transaction_action_keyboard
    async with AsyncSessionLocal() as session:
        user = await _get_user(session, callback.from_user)
        transactions = await get_recent(session, user.id, limit=8)

    if not transactions:
        await callback.message.edit_text(
            "📭 Hozircha tranzaksiyalar yo'q.",
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    lines = ["📋 *So'nggi tranzaksiyalar*\n"]
    for tx in transactions:
        emoji = "🔴" if tx.type.value == "expense" else "🟢"
        date_str = tx.created_at.strftime("%d.%m.%Y %H:%M")
        desc = f" — {tx.description}" if tx.description else ""
        lines.append(f"{emoji} *#{tx.id}* {format_amount(tx.amount)} | {tx.category}{desc} | {date_str}")

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


# ─── MENU: SETTINGS ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:settings")
async def cb_settings(callback: CallbackQuery) -> None:
    from keyboards.inline import settings_keyboard
    await callback.message.edit_text(
        "⚙️ *Sozlamalar*\n\n"
        "📌 *Bot haqida:*\n"
        "  Nomi: Finance Tracker Bot\n"
        "  Versiya: 2.0.0\n"
        "  Til: O'zbek 🇺🇿\n\n"
        "📌 *Buyruqlar:*\n"
        "  /start — Qayta boshlash\n"
        "  /balance — Tez balans\n"
        "  /report — Hisobotlar\n"
        "  /help — Yordam\n",
        parse_mode="Markdown",
        reply_markup=settings_keyboard(),
    )
    await callback.answer()
