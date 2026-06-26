"""Business logic: create an order, persist it, and fire the Telegram notification."""
from __future__ import annotations

from app.services.repository import Order, OrderItem, order_repo
from app.bot.notifier import send_order_notification


async def place_order(
    items: list[dict],
    total_price: float,
    table_number: int,
    currency: str,
    notify_chat_id: str,
) -> Order:
    order_items = [
        OrderItem(
            name=i["name"],
            price=i["price"],
            quantity=i["quantity"],
            currency=currency,
        )
        for i in items
    ]
    order = Order(
        items=order_items,
        total_price=total_price,
        table_number=table_number,
        currency=currency,
        notify_chat_id=notify_chat_id,
    )
    await order_repo.create(order)
    await send_order_notification(order)
    return order
