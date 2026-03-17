"""
Edit / Delete transaction handlers.
UX: compact list in ONE message → user types ID → action flow.
"""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import AsyncSessionLocal
from database.crud import get_transaction_by_id
from database.models import TransactionType
from keyboards.inline import (
    cancel_keyboard,
    confirm_keyboard,
    edit_category_expense_keyboard,
    edit_category_income_keyboard,
    edit_field_keyboard,
    main_menu_keyboard,
)
from services.finance_service import (
    edit_transaction,
    get_recent,
    register_user,
    remove_transaction,
)
from states.finance_states import EditTransactionStates
from utils.helpers import format_amount, parse_amount

router = Router()
logger = logging.getLogger(__name__)


async def _get_user(session, from_user):
    return await register_user(
        session, from_user.id, from_user.username, from_user.full_name
    )


def _build_list(transactions) -> str:
    lines = ["✏️ *Tranzaksiyalar ro'yxati*\n"]
    for tx in transactions:
        emoji = "🔴" if tx.type.value == "expense" else "🟢"
        date  = tx.created_at.strftime("%d.%m %H:%M")
        desc  = f" · {tx.description}" if tx.description else ""
        lines.append(
            f"{emoji} *#{tx.id}* — {format_amount(tx.amount)}\n"
            f"    {tx.category}{desc} | {date}"
        )
    lines.append("\n👇 Tahrirlash yoki o'chirish uchun *ID raqamini* yozing:")
    return "\n".join(lines)


def _action_keyboard(tx_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Tahrirlash", callback_data=f"tx_action:edit:{tx_id}")
    builder.button(text="🗑️ O'chirish",  callback_data=f"tx_action:delete:{tx_id}")
    builder.button(text="🔙 Orqaga",      callback_data="menu:edit_delete")
    builder.adjust(2, 1)
    return builder.as_markup()


@router.callback_query(F.data == "menu:edit_delete")
async def cb_edit_delete_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    async with AsyncSessionLocal() as session:
        user = await _get_user(session, callback.from_user)
        transactions = await get_recent(session, user.id, limit=10)

    if not transactions:
        await callback.message.edit_text(
            "📭 Hozircha tranzaksiyalar yo'q.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    await state.set_state(EditTransactionStates.waiting_tx_id)
    await callback.message.edit_text(
        _build_list(transactions),
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(EditTransactionStates.waiting_tx_id)
async def receive_tx_id(message: Message, state: FSMContext) -> None:
    text = message.text.strip().lstrip("#")
    if not text.isdigit():
        await message.answer(
            "⚠️ Faqat raqam kiriting. Masalan: `7`",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        return

    tx_id = int(text)
    async with AsyncSessionLocal() as session:
        user = await _get_user(session, message.from_user)
        tx = await get_transaction_by_id(session, tx_id, user.id)

    if tx is None:
        await message.answer(
            f"❌ *#{tx_id}* topilmadi. Boshqa ID kiriting:",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        return

    await state.update_data(tx_id=tx_id)
    emoji = "🔴" if tx.type.value == "expense" else "🟢"
    await message.answer(
        f"{emoji} *#{tx.id}* — {format_amount(tx.amount)}\n"
        f"  🏷️ {tx.category} | {tx.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"  📝 {tx.description or '—'}\n\n"
        "Quyidagi amalni tanlang:",
        parse_mode="Markdown",
        reply_markup=_action_keyboard(tx_id),
    )


@router.callback_query(F.data.startswith("tx_action:edit:"))
async def tx_action_edit(callback: CallbackQuery, state: FSMContext) -> None:
    tx_id = int(callback.data.split(":")[2])
    await state.update_data(tx_id=tx_id)
    await state.set_state(EditTransactionStates.waiting_field)
    await callback.message.edit_text(
        f"✏️ *#{tx_id}* — qaysi maydonni tahrirlaysiz?",
        parse_mode="Markdown",
        reply_markup=edit_field_keyboard(tx_id),
    )
    await callback.answer()


@router.callback_query(
    EditTransactionStates.waiting_field,
    F.data.startswith("edit_field:"),
)
async def edit_field_selected(callback: CallbackQuery, state: FSMContext) -> None:
    parts = callback.data.split(":")
    field = parts[1]
    tx_id = int(parts[2])
    await state.update_data(edit_field=field, tx_id=tx_id)
    await state.set_state(EditTransactionStates.waiting_new_value)

    if field == "amount":
        await callback.message.edit_text(
            "💵 Yangi miqdorni kiriting:", reply_markup=cancel_keyboard()
        )
    elif field == "description":
        await callback.message.edit_text(
            "📝 Yangi tavsifni kiriting:", reply_markup=cancel_keyboard()
        )
    elif field == "category":
        async with AsyncSessionLocal() as session:
            user = await _get_user(session, callback.from_user)
            tx   = await get_transaction_by_id(session, tx_id, user.id)
            tx_type = tx.type if tx else TransactionType.EXPENSE
        kb = (edit_category_expense_keyboard(tx_id)
              if tx_type == TransactionType.EXPENSE
              else edit_category_income_keyboard(tx_id))
        await callback.message.edit_text("🏷️ Yangi kategoriyani tanlang:", reply_markup=kb)
    await callback.answer()


@router.message(EditTransactionStates.waiting_new_value)
async def apply_edit_text(message: Message, state: FSMContext) -> None:
    data  = await state.get_data()
    field = data["edit_field"]
    tx_id = data["tx_id"]
    kwargs: dict = {}

    if field == "amount":
        amount = parse_amount(message.text)
        if amount is None:
            await message.answer("⚠️ Noto'g'ri miqdor. Qayta kiriting:", reply_markup=cancel_keyboard())
            return
        kwargs["amount"] = amount
    elif field == "description":
        kwargs["description"] = message.text

    async with AsyncSessionLocal() as session:
        user = await _get_user(session, message.from_user)
        tx   = await edit_transaction(session, tx_id, user.id, **kwargs)

    await state.clear()
    if tx:
        await message.answer(
            f"✅ *#{tx_id}* yangilandi!\n  {format_amount(tx.amount)} | {tx.category}",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await message.answer("❌ Xatolik yuz berdi.", reply_markup=main_menu_keyboard())


@router.callback_query(
    EditTransactionStates.waiting_new_value,
    F.data.startswith("edit_cat_expense:") | F.data.startswith("edit_cat_income:"),
)
async def apply_edit_category(callback: CallbackQuery, state: FSMContext) -> None:
    parts    = callback.data.split(":", 2)
    tx_id    = int(parts[1])
    category = parts[2]

    async with AsyncSessionLocal() as session:
        user = await _get_user(session, callback.from_user)
        tx   = await edit_transaction(session, tx_id, user.id, category=category)

    await state.clear()
    if tx:
        await callback.message.edit_text(
            f"✅ *#{tx_id}* kategoriya yangilandi: *{category}*",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await callback.message.edit_text("❌ Xatolik.", reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("tx_action:delete:"))
async def tx_action_delete(callback: CallbackQuery) -> None:
    tx_id = int(callback.data.split(":")[2])
    await callback.message.edit_text(
        f"🗑️ *#{tx_id}* tranzaksiyasini o'chirishni tasdiqlaysizmi?",
        parse_mode="Markdown",
        reply_markup=confirm_keyboard("delete", tx_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm:delete:"))
async def confirm_delete(callback: CallbackQuery, state: FSMContext) -> None:
    tx_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        user    = await _get_user(session, callback.from_user)
        deleted = await remove_transaction(session, tx_id, user.id)

    await state.clear()
    text = f"✅ *#{tx_id}* o'chirildi." if deleted else "❌ Topilmadi yoki sizga tegishli emas."
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    await callback.answer()