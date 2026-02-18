#!/usr/bin/env python3
"""
EightX Meme Generator
Composites top/bottom text onto a meme template image using classic meme styling.
Called by Claude after it has already downloaded the template via web_fetch.

Usage:
    python3 meme_generator.py <template_path> <output_path> [--top "TEXT"] [--bottom "TEXT"] [--font-size N]

Examples:
    python3 meme_generator.py template.png meme.png --top "When the CFO finds" --bottom "Hidden shipping costs"
    python3 meme_generator.py drake.png meme.png --top "" --bottom "Cash conversion cycle"
"""

import argparse
import os
import sys
import textwrap

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow --break-system-packages")
    sys.exit(1)


# Preferred fonts in order (Impact-like bold sans-serif)
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load the best available bold font."""
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    y_center: float,
    img_width: int,
    font: ImageFont.FreeTypeFont,
    font_size: int,
):
    """Draw outlined meme text centered at y_center."""
    if not text or not text.strip():
        return

    text = text.upper()
    max_chars = max(int(img_width / (font_size * 0.55)), 10)
    lines = textwrap.wrap(text, width=max_chars)

    # Measure
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])

    total_height = sum(line_heights) + (len(lines) - 1) * 8
    y = y_center - total_height / 2

    outline = max(2, font_size // 18)

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img_width - text_width) / 2

        # Black outline
        for dx in range(-outline, outline + 1):
            for dy in range(-outline, outline + 1):
                if dx * dx + dy * dy <= outline * outline + 1:
                    draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))

        # White fill
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_heights[i] + 8


def create_meme(
    template_path: str,
    output_path: str,
    top_text: str = "",
    bottom_text: str = "",
    font_size: int | None = None,
    max_width: int = 800,
) -> str:
    """
    Composite meme text onto a template image.

    Returns the output path on success.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    img = Image.open(template_path).convert("RGBA")

    # Scale to reasonable size
    if max(img.size) > max_width:
        ratio = max_width / max(img.size)
        img = img.resize(
            (int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS
        )

    # Auto font size
    if font_size is None:
        font_size = max(int(img.width / 14), 20)

    font = load_font(font_size)

    # Text overlay layer
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # Draw top and bottom text
    draw_text_block(draw, top_text, img.height * 0.10, img.width, font, font_size)
    draw_text_block(draw, bottom_text, img.height * 0.88, img.width, font, font_size)

    # Composite and save
    result = Image.alpha_composite(img, txt_layer).convert("RGB")
    result.save(output_path, "PNG", quality=95)

    return output_path


# --- Multi-panel meme support (Drake, expanding brain, etc.) ---

def create_multi_panel_meme(
    template_path: str,
    output_path: str,
    panel_texts: list[str],
    font_size: int | None = None,
    max_width: int = 800,
) -> str:
    """
    For multi-panel memes (Drake, Expanding Brain, etc.) where text goes
    beside or inside specific panels rather than top/bottom.

    panel_texts: List of strings, one per panel top-to-bottom.
    Text is placed on the RIGHT half of each equally-divided vertical panel.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    img = Image.open(template_path).convert("RGBA")

    if max(img.size) > max_width:
        ratio = max_width / max(img.size)
        img = img.resize(
            (int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS
        )

    if font_size is None:
        font_size = max(int(img.width / 22), 16)

    font = load_font(font_size)

    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    num_panels = len(panel_texts)
    panel_height = img.height / num_panels

    for i, text in enumerate(panel_texts):
        if not text or not text.strip():
            continue

        # Text goes on right half of each panel
        y_center = (i + 0.5) * panel_height
        text_area_width = img.width // 2

        text_upper = text.upper()
        max_chars = max(int(text_area_width / (font_size * 0.55)), 8)
        lines = textwrap.wrap(text_upper, width=max_chars)

        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])

        total_h = sum(line_heights) + (len(lines) - 1) * 6
        y = y_center - total_h / 2
        x_offset = img.width // 2

        outline = max(2, font_size // 18)

        for j, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = x_offset + (text_area_width - tw) / 2

            for dx in range(-outline, outline + 1):
                for dy in range(-outline, outline + 1):
                    if dx * dx + dy * dy <= outline * outline + 1:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
            y += line_heights[j] + 6

    result = Image.alpha_composite(img, txt_layer).convert("RGB")
    result.save(output_path, "PNG", quality=95)
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EightX Meme Generator")
    parser.add_argument("template", help="Path to meme template image")
    parser.add_argument("output", help="Output path for finished meme")
    parser.add_argument("--top", default="", help="Top text")
    parser.add_argument("--bottom", default="", help="Bottom text")
    parser.add_argument("--font-size", type=int, default=None, help="Font size override")
    parser.add_argument(
        "--panels",
        nargs="+",
        default=None,
        help="Panel texts for multi-panel memes (one per panel, top to bottom)",
    )

    args = parser.parse_args()

    if args.panels:
        result = create_multi_panel_meme(
            args.template, args.output, args.panels, args.font_size
        )
    else:
        result = create_meme(
            args.template, args.output, args.top, args.bottom, args.font_size
        )

    print(f"✅ Meme saved to: {result}")
