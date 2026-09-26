import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def create_gradient(width, height, c1, c2, c3):
    img = Image.new("RGB", (width, height), c1)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        # 3-stop vertical gradient
        t = y / max(1, height - 1)
        if t < 0.5:
            f = t * 2.0
            r = int(c1[0] + (c2[0] - c1[0]) * f)
            g = int(c1[1] + (c2[1] - c1[1]) * f)
            b = int(c1[2] + (c2[2] - c1[2]) * f)
        else:
            f = (t - 0.5) * 2.0
            r = int(c2[0] + (c3[0] - c2[0]) * f)
            g = int(c2[1] + (c3[1] - c2[1]) * f)
            b = int(c2[2] + (c3[2] - c2[2]) * f)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

def make_large_banner():
    # Recommended High-DPI size for Inno Setup 6 WizardImageFile: 328 x 628 (2x of 164x314)
    w, h = 328, 628
    bg = create_gradient(w, h, (11, 15, 25), (15, 23, 42), (10, 14, 26))
    draw = ImageDraw.Draw(bg, "RGBA")

    # Neon glow accents
    # Violet circle glow
    for i in range(50, 0, -5):
        alpha = int(120 * (1 - i / 50))
        draw.ellipse([w//2 - i*3, 200 - i*3, w//2 + i*3, 200 + i*3], fill=(121, 40, 202, alpha // 8))

    # Cyan circle glow
    for i in range(40, 0, -4):
        alpha = int(150 * (1 - i / 40))
        draw.ellipse([w//2 - i*2, 210 - i*2, w//2 + i*2, 210 + i*2], fill=(0, 210, 255, alpha // 8))

    # Decorative tech lines / grid
    grid_color = (0, 210, 255, 22)
    for x in range(0, w, 24):
        draw.line([(x, 0), (x, h)], fill=grid_color, width=1)
    for y in range(0, h, 24):
        draw.line([(0, y), (w, y)], fill=grid_color, width=1)

    # Slanted glow ribbon
    for offset in range(-8, 9):
        alpha = 80 - abs(offset) * 8
        draw.line([(0, 480 + offset), (w, 380 + offset)], fill=(0, 210, 255, alpha), width=2)
        draw.line([(0, 520 + offset), (w, 420 + offset)], fill=(121, 40, 202, alpha), width=2)

    # Paste app icon if exists
    icon_path = os.path.join(ASSETS_DIR, "icon.png")
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA")
        icon = icon.resize((128, 128), Image.Resampling.LANCZOS)
        bg.paste(icon, ((w - 128) // 2, 140), icon)

    # Load font or default
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arial.ttf", 14)
        font_ver = ImageFont.truetype("arialbd.ttf", 12)
    except Exception:
        font_large = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_ver = ImageFont.load_default()

    # Title text
    draw.text((w // 2, 300), "WinOptimizer", fill=(255, 255, 255), font=font_large, anchor="mm")
    draw.text((w // 2, 335), "GAMING & SYSTEM BOOSTER", fill=(0, 210, 255), font=font_ver, anchor="mm")
    draw.text((w // 2, 365), "Wersja 2.0 Pro", fill=(148, 163, 184), font=font_sub, anchor="mm")

    # Bottom badge
    draw.rectangle([30, h - 80, w - 30, h - 35], fill=(15, 23, 42), outline=(0, 210, 255), width=1)
    draw.text((w // 2, h - 58), "100% Offline • Zero Telemetrii", fill=(255, 255, 255), font=font_sub, anchor="mm")

    out_file = os.path.join(ASSETS_DIR, "wizard_large.bmp")
    bg.save(out_file, "BMP")
    print(f"Created: {out_file} ({w}x{h})")

def make_small_banner():
    # Recommended High-DPI size for WizardSmallImageFile: 110 x 110 (2x of 55x55)
    w, h = 110, 110
    bg = create_gradient(w, h, (11, 15, 25), (15, 23, 42), (10, 14, 26))
    draw = ImageDraw.Draw(bg, "RGBA")

    # Subtle cyan border
    draw.rectangle([0, 0, w - 1, h - 1], outline=(0, 210, 255, 80), width=1)

    icon_path = os.path.join(ASSETS_DIR, "icon.png")
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA")
        icon = icon.resize((72, 72), Image.Resampling.LANCZOS)
        bg.paste(icon, ((w - 72) // 2, (h - 72) // 2), icon)

    out_file = os.path.join(ASSETS_DIR, "wizard_small.bmp")
    bg.save(out_file, "BMP")
    print(f"Created: {out_file} ({w}x{h})")

if __name__ == "__main__":
    make_large_banner()
    make_small_banner()
