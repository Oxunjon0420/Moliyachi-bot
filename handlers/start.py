"""
/start and /help handlers. Shows inline main menu.
"""
import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from database.db import AsyncSessionLocal
from keyboards.inline import main_menu_keyboard
from services.finance_service import register_user

router = Router()
logger = logging.getLogger(__name__)


async def _send_main_menu(message: Message, text: str) -> None:
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with AsyncSessionLocal() as session:
        await register_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
    # Remove any lingering ReplyKeyboard first
    await message.answer("👋", reply_markup=ReplyKeyboardRemove())
    await _send_main_menu(
        message,
        f"Salom, *{message.from_user.first_name}*! 💼\n\n"
        "Men sizning shaxsiy moliyaviy yordamchingizman.\n"
        "Quyidagi menyudan boshlang 👇",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "📖 *Yordam*\n\n"
        "/start — Botni qayta ishga tushirish\n"
        "/balance — Tez balans\n"
        "/report — Hisobotlar\n"
        "/help — Ushbu yordam\n",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("balance"))
async def cmd_balance(message: Message) -> None:
    from services.finance_service import get_balance_summary
    from utils.helpers import format_amount
    async with AsyncSessionLocal() as session:
        from services.finance_service import register_user as ru
        user = await ru(session, message.from_user.id,
                        message.from_user.username, message.from_user.full_name)
        summary = await get_balance_summary(session, user.id)
    balance = summary["balance"]
    emoji = "🟢" if balance >= 0 else "🔴"
    await message.answer(
        "💳 *Joriy balans*\n\n"
        f"  🟢 Daromad:  {format_amount(summary['income'])}\n"
        f"  🔴 Xarajat:  {format_amount(summary['expense'])}\n"
        f"  {emoji} Saldo:    {format_amount(balance)}",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("report"))
async def cmd_report(message: Message) -> None:
    from keyboards.inline import reports_keyboard
    await message.answer(
        "📊 *Hisobot turini tanlang:*",
        parse_mode="Markdown",
        reply_markup=reports_keyboard(),
    )
