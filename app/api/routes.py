"""FastAPI route definitions."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from pathlib import Path

from app.services.order_service import place_order
from app.core.config import get_settings

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
settings = get_settings()


# ──────────────────────────────────────────────
# Pydantic schemas
# ──────────────────────────────────────────────

class CartItem(BaseModel):
    name: str
    price: float
    quantity: int = Field(ge=1)


class OrderPayload(BaseModel):
    items: list[CartItem] = Field(min_length=1)
    total_price: float = Field(gt=0)
    table_number: int = Field(ge=1, le=100)
    currency: str = "UZS"
    notify_chat_id: str = ""


class OrderResponse(BaseModel):
    success: bool
    order_id: str
    message: str


# ──────────────────────────────────────────────
# HTML entry point
# ──────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ──────────────────────────────────────────────
# Menu API
# ──────────────────────────────────────────────

MENU = [
    {"id": 1, "category": "Asosiy taomlar", "name": "Lavash", "name_en": "Lavash Wrap", "price_uzs": 35000, "price_eur": 3.50, "emoji": "🌯", "desc": "Toza go'sht, yangi sabzavotlar va maxsus sous bilan"},
    {"id": 2, "category": "Asosiy taomlar", "name": "Pizza Margarita", "name_en": "Pizza Margherita", "price_uzs": 75000, "price_eur": 7.50, "emoji": "🍕", "desc": "Italyan mozzarella, pomidor sousi, yangi reyhon"},
    {"id": 3, "category": "Asosiy taomlar", "name": "Burger Classic", "name_en": "Classic Burger", "price_uzs": 55000, "price_eur": 5.50, "emoji": "🍔", "desc": "Mol go'shti kotlet, salat, pomidor, maxsus sous"},
    {"id": 4, "category": "Asosiy taomlar", "name": "Shashlik", "name_en": "Shashlik", "price_uzs": 90000, "price_eur": 9.00, "emoji": "🍢", "desc": "Qo'zichoq go'shti, zira va ko'k piyoz bilan"},
    {"id": 5, "category": "Asosiy taomlar", "name": "Osh (Palov)", "name_en": "Plov", "price_uzs": 45000, "price_eur": 4.50, "emoji": "🍚", "desc": "An'anaviy o'zbek palovi, sabzi va mol go'shti bilan"},
    {"id": 6, "category": "Ichimliklar", "name": "Coca-Cola", "name_en": "Coca-Cola", "price_uzs": 12000, "price_eur": 1.20, "emoji": "🥤", "desc": "Sovuq, muzli — 0.5L"},
    {"id": 7, "category": "Ichimliklar", "name": "Limonada", "name_en": "Lemonade", "price_uzs": 18000, "price_eur": 1.80, "emoji": "🍋", "desc": "Uy limonadasi, nanadan tayyorlangan"},
    {"id": 8, "category": "Ichimliklar", "name": "Ko'k choy", "name_en": "Green Tea", "price_uzs": 8000, "price_eur": 0.80, "emoji": "🍵", "desc": "O'zbek ko'k choyi, qand bilan"},
    {"id": 9, "category": "Salatlar", "name": "Achichuk", "name_en": "Achichuk Salad", "price_uzs": 22000, "price_eur": 2.20, "emoji": "🥗", "desc": "Pomidor, piyoz va ko'k zira"},
    {"id": 10, "category": "Salatlar", "name": "Toshkent Salati", "name_en": "Tashkent Salad", "price_uzs": 30000, "price_eur": 3.00, "emoji": "🥙", "desc": "Qovurilgan mol go'shti, rediska, mayonez"},
    {"id": 11, "category": "Desertlar", "name": "Tiramisu", "name_en": "Tiramisu", "price_uzs": 40000, "price_eur": 4.00, "emoji": "🍰", "desc": "Italyan klassiği, qahva va mascarpone"},
    {"id": 12, "category": "Desertlar", "name": "Halva", "name_en": "Halva", "price_uzs": 15000, "price_eur": 1.50, "emoji": "🍬", "desc": "An'anaviy o'zbek halvasi, tarixiy retsept"},
]


@router.get("/api/menu")
async def get_menu():
    return {"menu": MENU, "categories": list(dict.fromkeys(i["category"] for i in MENU))}


# ──────────────────────────────────────────────
# Order API
# ──────────────────────────────────────────────

@router.post("/api/order", response_model=OrderResponse)
async def create_order(payload: OrderPayload):
    notify_chat_id = payload.notify_chat_id or settings.NOTIFY_CHAT_ID

    try:
        order = await place_order(
            items=[i.model_dump() for i in payload.items],
            total_price=payload.total_price,
            table_number=payload.table_number,
            currency=payload.currency,
            notify_chat_id=notify_chat_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Buyurtma yuborishda xato: {exc}")

    return OrderResponse(
        success=True,
        order_id=order.id,
        message="Buyurtmangiz qabul qilindi! Tez orada tayyorlanadi.",
    )
