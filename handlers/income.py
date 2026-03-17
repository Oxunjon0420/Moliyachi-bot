"""
Income flow — fully inline-based FSM.
"""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.db import AsyncSessionLocal
from keyboards.inline import (
    cancel_keyboard,
    description_keyboard,
    income_category_keyboard,
    main_menu_keyboard,
)
from services.finance_service import add_income, register_user
from states.finance_states import AddIncomeStates
from utils.helpers import format_amount, parse_amount

router = Router()
logger = logging.getLogger(__name__)


async def _get_user(session, from_user):
    return await register_user(
        session, from_user.id, from_user.username, from_user.full_name
    )


# ─── STEP 1: START ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:add_income")
async def start_add_income(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddIncomeStates.waiting_amount)
    await callback.message.edit_text(
        "💰 *Daromad qo'shish — 1/3*\n\n"
        "Miqdorni kiriting (masalan: `500000`):",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


# ─── STEP 2: AMOUNT → CATEGORY ───────────────────────────────────────────────

@router.message(AddIncomeStates.waiting_amount)
async def income_amount(message: Message, state: FSMContext) -> None:
    amount = parse_amount(message.text)
    if amount is None:
        await message.answer(
            "⚠️ Noto'g'ri miqdor. Musbat son kiriting.\nMasalan: `500000`",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        return

    await state.update_data(amount=amount)
    await state.set_state(AddIncomeStates.waiting_category)
    await message.answer(
        f"💰 *Daromad qo'shish — 2/3*\n\n"
        f"✅ Miqdor: *{format_amount(amount)}*\n\n"
        "Kategoriyani tanlang 👇",
        parse_mode="Markdown",
        reply_markup=income_category_keyboard(),
    )


# ─── STEP 3: CATEGORY → DESCRIPTION ─────────────────────────────────────────

@router.callback_query(
    AddIncomeStates.waiting_category,
    F.data.startswith("cat_income:"),
)
async def income_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = callback.data.split(":", 1)[1]
    await state.update_data(category=category)
    await state.set_state(AddIncomeStates.waiting_description)
    await callback.message.edit_text(
        f"💰 *Daromad qo'shish — 3/3*\n\n"
        f"🏷️ Kategoriya: *{category}*\n\n"
        "📝 Tavsif kiriting yoki o'tkazib yuboring:",
        parse_mode="Markdown",
        reply_markup=description_keyboard(),
    )
    await callback.answer()


# ─── SKIP DESCRIPTION (inline) ───────────────────────────────────────────────

@router.callback_query(
    AddIncomeStates.waiting_description,
    F.data == "desc:skip",
)
async def income_desc_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await _save_income(callback.message, state, callback.from_user, description=None, edit=True)
    await callback.answer()


# ─── DESCRIPTION TEXT ────────────────────────────────────────────────────────

@router.message(AddIncomeStates.waiting_description)
async def income_description(message: Message, state: FSMContext) -> None:
    await _save_income(message, state, message.from_user, description=message.text, edit=False)


# ─── SAVE ─────────────────────────────────────────────────────────────────────

async def _save_income(msg_obj, state, from_user, description, edit: bool) -> None:
    data = await state.get_data()
    async with AsyncSessionLocal() as session:
        user = await register_user(session, from_user.id, from_user.username, from_user.full_name)
        tx = await add_income(
            session,
            user_id=user.id,
            amount=data["amount"],
            category=data["category"],
            description=description,
        )
    await state.clear()

    text = (
        f"✅ *Daromad saqlandi!*\n\n"
        f"  💰 Miqdor: {format_amount(tx.amount)}\n"
        f"  🏷️ Kategoriya: {tx.category}\n"
        f"  📝 Tavsif: {tx.description or '—'}\n"
        f"  🆔 ID: #{tx.id}"
    )
    if edit:
        await msg_obj.edit_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    else:
        await msg_obj.answer(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
