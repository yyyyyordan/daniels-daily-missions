#!/usr/bin/env python3
"""Generate homescreen icons for Daniel's Daily Missions."""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def make_icon(size, maskable=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background: diagonal gradient from purple to pink.
    top = (91, 71, 224)     # #5b47e0
    mid = (159, 107, 255)   # #9f6bff
    bot = (255, 111, 179)   # #ff6fb3
    for y in range(size):
        t = y / (size - 1)
        if t < 0.55:
            c = lerp(top, mid, t / 0.55)
        else:
            c = lerp(mid, bot, (t - 0.55) / 0.45)
        draw.line([(0, y), (size, y)], fill=c + (255,))

    # Rounded corners (iOS applies its own mask, but PWA/Android benefit).
    # For maskable we leave it square; iOS touch icon gets clipped anyway.
    if not maskable:
        radius = int(size * 0.22)
        mask = Image.new("L", (size, size), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.rounded_rectangle([0, 0, size, size], radius=radius, fill=255)
        img.putalpha(mask)

    # Safe zone inset for maskable (icon content in inner 80%).
    inset = int(size * 0.1) if maskable else 0

    # Draw a glyph: a checkmark-star sparkle motif. Use a big bold "D!" instead
    # for readability on small homescreens.
    text = "D!"
    # Try a bold system font.
    font = None
    for path in [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/SFNSRounded.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ]:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, int(size * 0.52))
                break
            except Exception:
                continue
    if font is None:
        font = ImageFont.load_default()

    # Draw a subtle white circle behind the text for punch.
    cx, cy = size // 2, size // 2
    r = int(size * 0.34)
    circle_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(circle_layer)
    cdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 60))
    img = Image.alpha_composite(img, circle_layer)

    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (size - tw) // 2 - bbox[0]
    ty = (size - th) // 2 - bbox[1] - int(size * 0.02)
    # Soft shadow.
    draw.text((tx + max(2, size // 120), ty + max(2, size // 120)), text,
              font=font, fill=(30, 20, 80, 120))
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))

    # A little sparkle in the corner.
    sp = int(size * 0.12)
    sx, sy = int(size * 0.72), int(size * 0.22)
    spark = [
        (sx, sy - sp),
        (sx + sp * 0.25, sy - sp * 0.25),
        (sx + sp, sy),
        (sx + sp * 0.25, sy + sp * 0.25),
        (sx, sy + sp),
        (sx - sp * 0.25, sy + sp * 0.25),
        (sx - sp, sy),
        (sx - sp * 0.25, sy - sp * 0.25),
    ]
    draw.polygon(spark, fill=(255, 215, 100, 230))

    return img

targets = [
    ("icon-180.png", 180, False),
    ("icon-192.png", 192, False),
    ("icon-512.png", 512, False),
    ("icon-512-maskable.png", 512, True),
]
for name, sz, mask in targets:
    out = make_icon(sz, maskable=mask)
    out.save(os.path.join(HERE, name), "PNG")
    print("wrote", name, sz)
