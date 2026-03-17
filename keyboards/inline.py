"""
All InlineKeyboard builders for Finance Tracker Bot.
Single source of truth for every keyboard in the bot.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import EXPENSE_CATEGORIES, INCOME_CATEGORIES


# ─── MAIN MENU ────────────────────────────────────────────────────────────────

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main inline menu."""
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Xarajat qo'shish",       callback_data="menu:add_expense")
    builder.button(text="💰 Daromad qo'shish",        callback_data="menu:add_income")
    builder.button(text="💳 Balans",                  callback_data="menu:balance")
    builder.button(text="📊 Hisobotlar",              callback_data="menu:reports")
    builder.button(text="📋 So'nggi tranzaksiyalar",  callback_data="menu:recent")
    builder.button(text="✏️ Tahrirlash / O'chirish",  callback_data="menu:edit_delete")
    builder.button(text="🤖 AI Maslahat",             callback_data="menu:ai")
    builder.button(text="⚙️ Sozlamalar",              callback_data="menu:settings")
    builder.adjust(2, 2, 2, 2)
    return builder.as_markup()


# ─── REPORTS ──────────────────────────────────────────────────────────────────

def reports_keyboard() -> InlineKeyboardMarkup:
    """Report type selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Bugungi",          callback_data="report:daily")
    builder.button(text="📆 Haftalik",          callback_data="report:weekly")
    builder.button(text="🗓️ Oylik",             callback_data="report:monthly")
    builder.button(text="📈 Kategoriyalar",     callback_data="report:categories")
    builder.button(text="🔙 Orqaga",            callback_data="nav:main_menu")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


# ─── CATEGORIES ───────────────────────────────────────────────────────────────

def expense_category_keyboard() -> InlineKeyboardMarkup:
    """Expense category selection."""
    builder = InlineKeyboardBuilder()
    for cat in EXPENSE_CATEGORIES:
        builder.button(text=cat.value, callback_data=f"cat_expense:{cat.value}")
    builder.button(text="❌ Bekor qilish", callback_data="nav:cancel")
    builder.adjust(2)
    return builder.as_markup()


def income_category_keyboard() -> InlineKeyboardMarkup:
    """Income category selection."""
    builder = InlineKeyboardBuilder()
    for cat in INCOME_CATEGORIES:
        builder.button(text=cat.value, callback_data=f"cat_income:{cat.value}")
    builder.button(text="❌ Bekor qilish", callback_data="nav:cancel")
    builder.adjust(2)
    return builder.as_markup()


# ─── DESCRIPTION STEP ─────────────────────────────────────────────────────────

def description_keyboard() -> InlineKeyboardMarkup:
    """Skip / Cancel for description step."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⏭️ O'tkazib yuborish", callback_data="desc:skip"),
        InlineKeyboardButton(text="❌ Bekor qilish",       callback_data="nav:cancel"),
    ]])


# ─── CANCEL ONLY ──────────────────────────────────────────────────────────────

def cancel_keyboard() -> InlineKeyboardMarkup:
    """Single cancel button."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="nav:cancel"),
    ]])


# ─── BACK TO MENU ─────────────────────────────────────────────────────────────

def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Single back-to-menu button."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="nav:main_menu"),
    ]])


# ─── CONFIRM / DELETE ─────────────────────────────────────────────────────────

def confirm_keyboard(action: str, tx_id: int) -> InlineKeyboardMarkup:
    """Yes/No confirmation keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha",   callback_data=f"confirm:{action}:{tx_id}"),
        InlineKeyboardButton(text="❌ Yo'q", callback_data="nav:cancel"),
    ]])


# ─── TRANSACTION ACTIONS ──────────────────────────────────────────────────────

def transaction_action_keyboard(tx_id: int) -> InlineKeyboardMarkup:
    """Edit / Delete buttons for a transaction."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"tx_action:edit:{tx_id}"),
        InlineKeyboardButton(text="🗑️ O'chirish",  callback_data=f"tx_action:delete:{tx_id}"),
    ]])


def edit_field_keyboard(tx_id: int) -> InlineKeyboardMarkup:
    """Which field to edit."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 Miqdor",     callback_data=f"edit_field:amount:{tx_id}"),
            InlineKeyboardButton(text="🏷️ Kategoriya", callback_data=f"edit_field:category:{tx_id}"),
        ],
        [
            InlineKeyboardButton(text="📝 Tavsif",     callback_data=f"edit_field:description:{tx_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="nav:cancel"),
        ],
    ])


def edit_category_expense_keyboard(tx_id: int) -> InlineKeyboardMarkup:
    """Expense category selection during edit."""
    builder = InlineKeyboardBuilder()
    for cat in EXPENSE_CATEGORIES:
        builder.button(text=cat.value, callback_data=f"edit_cat_expense:{tx_id}:{cat.value}")
    builder.button(text="❌ Bekor qilish", callback_data="nav:cancel")
    builder.adjust(2)
    return builder.as_markup()


def edit_category_income_keyboard(tx_id: int) -> InlineKeyboardMarkup:
    """Income category selection during edit."""
    builder = InlineKeyboardBuilder()
    for cat in INCOME_CATEGORIES:
        builder.button(text=cat.value, callback_data=f"edit_cat_income:{tx_id}:{cat.value}")
    builder.button(text="❌ Bekor qilish", callback_data="nav:cancel")
    builder.adjust(2)
    return builder.as_markup()


# ─── AI ADVISOR ───────────────────────────────────────────────────────────────

def ai_advisor_keyboard() -> InlineKeyboardMarkup:
    """AI advisor action buttons."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗑️ Suhbatni tozalash", callback_data="ai:clear"),
            InlineKeyboardButton(text="🏠 Chiqish",            callback_data="nav:main_menu"),
        ]
    ])


# ─── SETTINGS ─────────────────────────────────────────────────────────────────

def settings_keyboard() -> InlineKeyboardMarkup:
    """Settings menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="nav:main_menu")],
    ])
