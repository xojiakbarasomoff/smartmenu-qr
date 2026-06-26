"""Telegram bot command and message handlers."""
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    chat_id = message.chat.id
    user_name = message.from_user.full_name if message.from_user else "Do'stim"

    text = (
        f"👋 Salom, *{user_name}\\!*\n\n"
        f"🤖 Men *SmartMenu QR* botman\\!\n\n"
        f"📋 *Restoran egasi uchun:*\n"
        f"Buyurtmalarni qabul qilish uchun quyidagi Chat ID ni "
        f"`.env` faylidagi `NOTIFY_CHAT_ID` ga kiriting:\n\n"
        f"```\n{chat_id}\n```\n\n"
        f"✅ Shu chat ID ni nusxa ko'chirib `.env` fayliga qo'shing, "
        f"shunda barcha buyurtmalar shu chatga keladi\\!"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2)


@router.message(Command("chatid"))
async def cmd_chatid(message: types.Message) -> None:
    chat_id = message.chat.id
    text = (
        f"🆔 *Sizning Chat ID:*\n\n"
        f"```\n{chat_id}\n```\n\n"
        f"Bu ID ni `.env` faylidagi `NOTIFY_CHAT_ID` ga kiriting\\."
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2)


@router.message()
async def echo_chat_id(message: types.Message) -> None:
    chat_id = message.chat.id
    text = (
        f"📨 Xabar qabul qilindi\\!\n\n"
        f"🆔 Bu chatning ID si: `{chat_id}`\n\n"
        f"_Bu ID ni buyurtmalarni qabul qilish uchun ishlatishingiz mumkin\\._"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2)
