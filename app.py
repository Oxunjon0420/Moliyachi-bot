"""
Finance Tracker Bot v2 — fully inline UX.
Run: python app.py
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config, setup_logging
from database.db import init_db
from handlers import start, expense, income, settings, ai_advisor, menu_callbacks

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    logger.info("Starting Finance Tracker Bot v2...")
    config.validate()
    await init_db()

    bot = Bot(token=config.BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    # Order matters: FSM-heavy routers first, then general menu callbacks
    dp.include_router(start.router)
    dp.include_router(expense.router)
    dp.include_router(income.router)
    dp.include_router(settings.router)
    dp.include_router(ai_advisor.router)
    dp.include_router(menu_callbacks.router)   # catches nav: / menu: / report: callbacks

    logger.info("Bot is running. Press Ctrl+C to stop.")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
