#!/usr/bin/env python3
"""
SmartMenu QR Code Generator
════════════════════════════════════════════════════════════
Generates 20 print-ready QR code cards for tables 1 – 20.
Each PNG encodes the table URL so the web-app auto-selects
the correct table when scanned.

Usage
-----
  python generate_qr.py                          # localhost:8000
  python generate_qr.py https://yourdomain.com   # production URL

Output
------
  output_qrcodes/
    table_01_qr.png  …  table_20_qr.png   (300 DPI, print-ready)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# ── Auto-install missing dependencies ────────────────────────────
def _ensure(pkg: str, import_name: str | None = None) -> None:
    try:
        __import__(import_name or pkg)
    except ImportError:
        print(f"  📦 Installing {pkg} …")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pkg, "-q"],
            stdout=subprocess.DEVNULL,
        )


_ensure("qrcode[pil]", "qrcode")
_ensure("Pillow", "PIL")

# ── Now safe to import ────────────────────────────────────────────
import qrcode
from PIL import Image, ImageDraw, ImageFont


# ── Font loader (cross-platform) ─────────────────────────────────
_FONT_SEARCH = [
    # Windows
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    # Linux (Docker)
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    # macOS
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
]


def _font(size: int) -> ImageFont.ImageFont:
    for path in _FONT_SEARCH:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    # Absolute last resort
    return ImageFont.load_default()


def _text_w(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    """Return pixel width of rendered text (Pillow 9+ and older)."""
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]
    except AttributeError:
        return draw.textlength(text, font=font)  # Pillow 8.x


# ─────────────────────────────────────────────────────────────────
def generate_card(base_url: str, table: int, out_dir: Path) -> Path:
    """
    Build one premium QR-card image and save it to *out_dir*.

    Layout (top → bottom)
    ─────────────────────
    8 px   gold accent bar
    24 px  top padding
    QR     centred, high error-correction
    20 px  gap
    1 px   divider
    18 px  gap
    text   "SmartMenu"
    10 px  gap
    text   "STOL N"  (gold, large)
    14 px  gap
    text   scan hint (grey, small)
    20 px  bottom padding
    8 px   gold accent bar
    """
    url = f"{base_url.rstrip('/')}/?table={table}"

    # ── QR generation ────────────────────────────────────────────
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=18,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#000000", back_color="#FFFFFF").convert("RGB")
    qr_w, qr_h = qr_img.size

    # ── Card canvas ──────────────────────────────────────────────
    GOLD      = "#D4AF37"
    PAD_H     = 48          # left/right padding inside card
    TOP_BAR   = 8
    BOT_BAR   = 8
    TOP_PAD   = 24          # space between gold bar and QR
    GAP_AFTER = 20          # space between QR and divider
    LABEL_H   = 160         # total height reserved for text area

    card_w = qr_w + PAD_H * 2
    card_h = TOP_BAR + TOP_PAD + qr_h + GAP_AFTER + LABEL_H + BOT_BAR

    card = Image.new("RGB", (card_w, card_h), "#FFFFFF")

    # Gold top bar
    card.paste(Image.new("RGB", (card_w, TOP_BAR), GOLD), (0, 0))

    # QR centred
    qr_x = PAD_H
    qr_y = TOP_BAR + TOP_PAD
    card.paste(qr_img, (qr_x, qr_y))

    draw = ImageDraw.Draw(card)
    f_name  = _font(26)
    f_table = _font(38)
    f_hint  = _font(17)

    # Divider line
    div_y = qr_y + qr_h + GAP_AFTER
    draw.line(
        [(PAD_H + 20, div_y), (card_w - PAD_H - 20, div_y)],
        fill="#EBEBEB", width=1,
    )

    y = div_y + 18

    # Restaurant name
    t_name = "SmartMenu"
    tw = _text_w(draw, t_name, f_name)
    draw.text(((card_w - tw) // 2, y), t_name, font=f_name, fill="#1A1A1A")
    y += 38

    # Table number (gold, prominent)
    t_table = f"STOL  {table}"
    tw2 = _text_w(draw, t_table, f_table)
    draw.text(((card_w - tw2) // 2, y), t_table, font=f_table, fill=GOLD)
    y += 52

    # Scan hint
    t_hint = "Menyuni ko'rish uchun skanerlang"
    tw3 = _text_w(draw, t_hint, f_hint)
    draw.text(((card_w - tw3) // 2, y), t_hint, font=f_hint, fill="#AAAAAA")

    # Gold bottom bar
    card.paste(Image.new("RGB", (card_w, BOT_BAR), GOLD), (0, card_h - BOT_BAR))

    # ── Save at 300 DPI ──────────────────────────────────────────
    out_path = out_dir / f"table_{table:02d}_qr.png"
    card.save(str(out_path), "PNG", dpi=(300, 300))
    return out_path


# ─────────────────────────────────────────────────────────────────
def main() -> None:
    base_url  = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    out_dir   = Path("output_qrcodes")
    out_dir.mkdir(exist_ok=True)

    SEP = "-" * 50
    print(f"\n[SmartMenu] QR Code Generator")
    print(SEP)
    print(f"  Base URL  :  {base_url}")
    print(f"  Tables    :  1 - 20")
    print(f"  Output    :  {out_dir}/")
    print(f"  Quality   :  300 DPI  |  H error correction")
    print(SEP + "\n")

    paths: list[Path] = []
    for i in range(1, 21):
        p = generate_card(base_url, i, out_dir)
        print(f"  [OK]  Stol {i:>2}  ->  {p.name}")
        paths.append(p)

    # Quick sanity check on first file
    first   = paths[0]
    size_kb = first.stat().st_size // 1024
    img     = Image.open(first)

    print(f"\n{SEP}")
    print(f"  DONE: {len(paths)} QR kartochka yaratildi  ->  '{out_dir}/'")
    print(f"  Size     :  {img.size[0]} x {img.size[1]} px")
    print(f"  File (~1):  ~{size_kb} KB")
    print(f"  Print    :  300 DPI - bosib chiqarishga tayyor!")
    print(f"\n  TIP: Laminatsiya qilib har bir stolga qo'ying.")
    print(f"  URL ex : {base_url.rstrip('/')}/?table=5\n")


if __name__ == "__main__":
    main()
