"""Genera las imágenes para compartir (Open Graph / Twitter): assets/og-confy-es.png y -en.png, 1200×630.

Uso:  python og_images.py        (necesita Pillow y fontTools+brotli para leer las fuentes .woff2 del sitio)
Usa solo las fuentes y el ícono que ya están en el repo; el texto es el del hero de cada home.
"""
import io
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
W, H = 1200, 630
FOREST, BAND2, BRAND, WHITE, MUTED = (27, 67, 50), (15, 48, 37), (29, 210, 188), (241, 247, 245), (169, 196, 188)


def ttf_bytes(woff2):
    f = TTFont(ROOT / "fonts" / woff2)
    f.flavor = None
    buf = io.BytesIO()
    f.save(buf)
    return buf.getvalue()


INTER = ttf_bytes("inter-latin.woff2")
SERIF = ttf_bytes("instrument-serif-italic-latin.woff2")
MONO = ttf_bytes("jetbrains-mono-latin.woff2")


def font(data, size, weight=None):
    f = ImageFont.truetype(io.BytesIO(data), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def gradient():
    img = Image.new("RGB", (W, H), FOREST)
    px = img.load()
    for x in range(W):
        t = x / (W - 1)
        c = tuple(int(FOREST[i] * (1 - t) + BAND2[i] * t) for i in range(3))
        for y in range(H):
            px[x, y] = c
    return img


def headline(draw, parts, x, y, max_w, size):
    """parts: [(texto, 'sans'|'serif')]. Parte en líneas por ancho y dibuja."""
    sans, serif = font(INTER, size, 600), font(SERIF, int(size * 1.12))
    words = []
    for text, kind in parts:
        for w in text.split():
            words.append((w, kind))
    lines, cur, cur_w = [], [], 0
    space = draw.textlength(" ", font=sans)
    for w, kind in words:
        f = serif if kind == "serif" else sans
        wl = draw.textlength(w, font=f)
        if cur and cur_w + space + wl > max_w:
            lines.append(cur)
            cur, cur_w = [], 0
        cur.append((w, kind, wl))
        cur_w += (space if len(cur) > 1 else 0) + wl
    lines.append(cur)
    lh = int(size * 1.12)
    for i, line in enumerate(lines):
        cx = x
        for w, kind, wl in line:
            f = serif if kind == "serif" else sans
            draw.text((cx, y + i * lh), w, font=f, fill=BRAND if kind == "serif" else WHITE)
            cx += wl + space
    return y + len(lines) * lh


def make(lang, eyebrow, parts, tagline):
    img = gradient()
    d = ImageDraw.Draw(img)
    icon = Image.open(ROOT / "assets" / "apple-touch-icon.png").convert("RGBA").resize((88, 88), Image.LANCZOS)
    img.paste(icon, (72, 60), icon)
    d.text((176, 74), "Confy", font=font(INTER, 54, 600), fill=WHITE)
    d.text((72, 190), eyebrow.upper(), font=font(MONO, 24), fill=BRAND)
    end = headline(d, parts, 72, 244, W - 144, 80)
    d.text((72, H - 78), "appconfy.com", font=font(MONO, 28), fill=BRAND)
    tl = font(INTER, 28, 500)
    d.text((W - 72 - d.textlength(tagline, font=tl), H - 80), tagline, font=tl, fill=MUTED)
    assert end < H - 110, f"{lang}: el titular no cabe"
    out = ROOT / "assets" / f"og-confy-{lang}.png"
    img.save(out, optimize=True)
    print(out.name, img.size, out.stat().st_size, "bytes")


make("es", "Para negocios que reciben transferencias Bancolombia",
     [("Que ningún comprobante falso te", "sans"), ("engañe", "serif"), ("otra vez.", "sans")],
     "Verifica comprobantes de Bancolombia")
make("en", "For businesses that take Bancolombia transfers",
     [("Never get", "sans"), ("fooled", "serif"), ("by a fake receipt again.", "sans")],
     "Verify Bancolombia receipts")
