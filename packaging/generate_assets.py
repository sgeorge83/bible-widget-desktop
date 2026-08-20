"""Generate Microsoft Store logos, tiles, and the Windows .ico from WordOnAir art."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(__file__).resolve().parent / "Assets"
ICON_SRC = ROOT / "widget" / "assets" / "wordonair-icon.png"
MARK_SRC = ROOT / "widget" / "assets" / "wordonair-mark.png"

NAVY = (18, 38, 72, 255)
GOLD = (212, 168, 83, 255)
WHITE = (248, 250, 253, 255)
TEAL = (94, 196, 207, 255)


def load_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def rounded_mask(size: int, radius: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    return mask


def canvas(width: int, height: int) -> Image.Image:
    img = Image.new("RGBA", (width, height), NAVY)
    return img


def paste_centered(base: Image.Image, overlay: Image.Image, max_ratio: float = 0.72) -> None:
    bw, bh = base.size
    side = int(min(bw, bh) * max_ratio)
    overlay = overlay.resize((side, side), Image.Resampling.LANCZOS)
    x = (bw - side) // 2
    y = (bh - side) // 2
    base.alpha_composite(overlay, (x, y))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def save_png(img: Image.Image, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    dest = ASSETS / name
    img.convert("RGBA").save(dest, format="PNG")
    print(f"Wrote {dest}")


def square_logo(src: Image.Image, size: int, name: str, radius: int | None = None) -> None:
    img = canvas(size, size)
    paste_centered(img, src, 0.78)
    if radius:
        mask = rounded_mask(size, radius)
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        out.paste(img, (0, 0))
        out.putalpha(mask)
        img = out
    save_png(img, name)


def wide_tile(icon: Image.Image, mark: Image.Image) -> None:
    img = canvas(310, 150)
    # Left emblem
    emblem = icon.resize((96, 96), Image.Resampling.LANCZOS)
    img.alpha_composite(emblem, (28, 27))
    draw = ImageDraw.Draw(img)
    draw.text((140, 42), "Bible Widget", font=font(26, bold=True), fill=WHITE)
    draw.text((140, 82), "Verse of the Day", font=font(16), fill=GOLD)
    save_png(img, "Wide310x150Logo.png")


def splash(icon: Image.Image) -> None:
    img = canvas(620, 300)
    paste_centered(img, icon, 0.38)
    draw = ImageDraw.Draw(img)
    try:
        draw.text((310, 238), "Bible Widget — Verse of the Day", font=font(24, bold=True), fill=WHITE, anchor="mm")
        draw.text((310, 272), "WordOnAir Labs", font=font(16), fill=GOLD, anchor="mm")
    except TypeError:
        draw.text((120, 226), "Bible Widget — Verse of the Day", font=font(22, bold=True), fill=WHITE)
        draw.text((230, 262), "WordOnAir Labs", font=font(16), fill=GOLD)
    save_png(img, "SplashScreen.png")


def app_ico(hires: Image.Image) -> None:
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = [hires.resize(size, Image.Resampling.LANCZOS) for size in sizes]
    dest = ASSETS / "app.ico"
    images[-1].save(dest, format="ICO", sizes=sizes)
    print(f"Wrote {dest}")


def main() -> None:
    icon = load_rgba(ICON_SRC if ICON_SRC.exists() else MARK_SRC)
    mark = load_rgba(MARK_SRC) if MARK_SRC.exists() else icon

    square_logo(icon, 44, "Square44x44Logo.png")
    square_logo(icon, 50, "StoreLogo.png")
    square_logo(icon, 71, "Square71x71Logo.png")
    square_logo(icon, 150, "Square150x150Logo.png", radius=24)
    square_logo(icon, 310, "Square310x310Logo.png", radius=48)
    wide_tile(icon, mark)
    splash(icon)
    hires = canvas(256, 256)
    paste_centered(hires, icon, 0.86)
    app_ico(hires)


if __name__ == "__main__":
    main()
