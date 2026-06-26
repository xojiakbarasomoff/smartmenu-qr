"""
Unified entry point — runs FastAPI (uvicorn) + aiogram polling concurrently
on a single asyncio event loop.

Usage:
    python run.py
"""
import asyncio
import logging
import os

import uvicorn

from app.core.config import get_settings
from app.main import app
from app.bot.instance import bot, dp
from app.bot import handlers  # registers the router via import

settings = get_settings()

# Render (and most PaaS providers) inject $PORT dynamically.
# Fall back to the value in .env / settings for local development.
_PORT = int(os.environ.get("PORT", settings.APP_PORT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("smartmenu")


async def run_fastapi() -> None:
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",   # required on Render — bind to all interfaces
        port=_PORT,
        log_level="info",
        loop="none",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_bot() -> None:
    dp.include_router(handlers.router)
    log.info("Telegram bot polling started — @my_smart_menu_bot")
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        await bot.session.close()


async def main() -> None:
    log.info("=" * 55)
    log.info("  SmartMenu QR — Starting up")
    log.info(f"  Web UI  → http://localhost:{_PORT}")
    log.info(f"  Bot     → {settings.BOT_USERNAME}")
    if not settings.NOTIFY_CHAT_ID:
        log.warning(
            "  NOTIFY_CHAT_ID is not set! Start the bot on Telegram, "
            "send /start, copy your Chat ID, and add it to .env"
        )
    log.info("=" * 55)
    await asyncio.gather(run_fastapi(), run_bot())


if __name__ == "__main__":
    asyncio.run(main())
