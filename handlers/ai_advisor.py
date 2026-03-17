"""
AI Advisor handler — OpenRouter/OpenAI GPT, fully inline buttons.
"""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config.config import config
from keyboards.inline import ai_advisor_keyboard, main_menu_keyboard
from states.finance_states import AiAdvisorStates

from openai import AsyncOpenAI

router = Router()
logger = logging.getLogger(__name__)

AI_SYSTEM_PROMPT = """Siz "Finance Tracker Bot" ning AI moliyaviy maslahatchisissiz.
Foydalanuvchilarga shaxsiy moliya, byudjet rejalashtirish, tejash, investitsiya 
va xarajatlarni kamaytirish bo'yicha O'zbek tilida professional maslahat bering.
Javoblarni qisqa, aniq va amaliy qiling. Emoji ishlatishingiz mumkin.
Agar savol moliya bilan bog'liq bo'lmasa, muloyimlik bilan moliyaviy mavzularga yo'naltiring."""


# ─── ENTRY (from inline menu) ─────────────────────────────────────────────────

@router.callback_query(F.data == "menu:ai")
async def start_ai_advisor(callback: CallbackQuery, state: FSMContext) -> None:
    if not config.OPENAI_API_KEY:
        await callback.message.edit_text(
            "⚠️ OpenAI/OpenRouter API kaliti sozlanmagan.\n"
            "`.env` fayliga `OPENAI_API_KEY=...` qo'shing.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    await state.set_state(AiAdvisorStates.chatting)
    await state.update_data(history=[])
    await callback.message.edit_text(
        "🤖 *AI Moliyaviy Maslahatchi*\n\n"
        "Salom! Men sizning shaxsiy AI moliyaviy maslahatchangizman. 💼\n\n"
        "📌 *Nima so'rashingiz mumkin:*\n"
        "  • Byudjet rejalashtirish\n"
        "  • Xarajatlarni kamaytirish\n"
        "  • Tejash strategiyalari\n"
        "  • Investitsiya asoslari\n"
        "  • Moliyaviy maqsad qo'yish\n\n"
        "Savolingizni yozing 👇",
        parse_mode="Markdown",
        reply_markup=ai_advisor_keyboard(),
    )
    await callback.answer()


# ─── CLEAR HISTORY ────────────────────────────────────────────────────────────

@router.callback_query(AiAdvisorStates.chatting, F.data == "ai:clear")
async def clear_ai_history(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(history=[])
    await callback.message.edit_text(
        "🗑️ Suhbat tarixi tozalandi.\n\nYangi savol bering 👇",
        reply_markup=ai_advisor_keyboard(),
    )
    await callback.answer()


# ─── HANDLE USER MESSAGES ─────────────────────────────────────────────────────

@router.message(AiAdvisorStates.chatting)
async def ai_chat(message: Message, state: FSMContext) -> None:
    user_text = message.text.strip() if message.text else ""
    if not user_text:
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    data = await state.get_data()
    history: list[dict] = data.get("history", [])
    history.append({"role": "user", "content": user_text})
    trimmed = history[-10:]

    try:
        client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        response = await client.chat.completions.create(
            model="arcee-ai/trinity-large-preview:free",
            messages=[
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                *trimmed,
            ],
            max_tokens=600,
            temperature=0.7,
        )
        ai_reply = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": ai_reply})
        await state.update_data(history=history)

        await message.answer(
            f"🤖 {ai_reply}",
            reply_markup=ai_advisor_keyboard(),
        )

    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        await message.answer(
            f"⚠️ AI javob bera olmadi. Qaytadan urinib ko'ring.\nXato: `{type(e).__name__}`",
            parse_mode="Markdown",
            reply_markup=ai_advisor_keyboard(),
        )
