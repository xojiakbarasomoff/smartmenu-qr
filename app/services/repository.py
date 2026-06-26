"""
In-memory async repository — swap the store dict for a Supabase/PostgreSQL
async client later without changing any call sites.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class OrderItem:
    name: str
    price: float
    quantity: int
    currency: str = "UZS"


@dataclass
class Order:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    table_number: int = 0
    items: list[OrderItem] = field(default_factory=list)
    total_price: float = 0.0
    currency: str = "UZS"
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    notify_chat_id: str = ""


class OrderRepository:
    def __init__(self) -> None:
        self._store: dict[str, Order] = {}

    async def create(self, order: Order) -> Order:
        self._store[order.id] = order
        return order

    async def get(self, order_id: str) -> Order | None:
        return self._store.get(order_id)

    async def list_all(self) -> list[Order]:
        return sorted(self._store.values(), key=lambda o: o.created_at, reverse=True)

    async def update_status(self, order_id: str, status: str) -> Order | None:
        order = self._store.get(order_id)
        if order:
            order.status = status
        return order


# Singleton — shared across the whole process
order_repo = OrderRepository()
