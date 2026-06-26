"""Sends a beautifully formatted MarkdownV2 order notification to Telegram."""
from __future__ import annotations

import re
from app.services.repository import Order
from app.core.config import get_settings


def _escape(text: str) -> str:
    """Escape special MarkdownV2 characters."""
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!\\])", r"\\\1", str(text))


async def send_order_notification(order: Order) -> None:
    from app.bot.instance import bot

    settings = get_settings()
    chat_id = order.notify_chat_id or settings.NOTIFY_CHAT_ID

    if not chat_id:
        return

    currency_symbol = "€" if order.currency == "EUR" else "so'm"

    lines = [
        "🍽 *YANGI BUYURTMA KELDI\\!*",
        "",
        f"🪑 *Stol raqami:* `{_escape(order.table_number)}`",
        f"🆔 *Buyurtma ID:* `{_escape(order.id[:8].upper())}`",
        "",
        "━━━━━━━━━━━━━━━━━━━",
        "📋 *Buyurtma tarkibi:*",
        "",
    ]

    for item in order.items:
        item_total = item.price * item.quantity
        if order.currency == "EUR":
            price_str = f"€{item.price:.2f} × {item.quantity} = €{item_total:.2f}"
        else:
            price_str = (
                f"{int(item.price):,} so'm × {item.quantity} = {int(item_total):,} so'm"
            )
        lines.append(f"▪️ *{_escape(item.name)}* — {_escape(price_str)}")

    lines += [
        "",
        "━━━━━━━━━━━━━━━━━━━",
    ]

    if order.currency == "EUR":
        total_str = f"€{order.total_price:.2f}"
    else:
        total_str = f"{int(order.total_price):,} so'm"

    lines += [
        f"💰 *JAMI:* `{_escape(total_str)}`",
        "",
        "⏰ *Iltimos, buyurtmani tayyorlang\\!*",
    ]

    message = "\n".join(lines)
    await bot.send_message(chat_id=int(chat_id), text=message)
