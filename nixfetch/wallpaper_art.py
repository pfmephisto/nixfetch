"""
Render a wallpaper image as Unicode half-block pixel art using Rich Text.
"""

from rich.text import Text


def render_wallpaper(image_path: str, width: int = 40, height: int = 24) -> list[Text] | None:
    """Load an image and render it as colored Unicode half-blocks.

    Each character represents two vertical pixels using the upper half-block '▀',
    with fg = top pixel color and bg = bottom pixel color.

    Returns a list of Rich Text lines, or None if the image can't be loaded.
    """
    try:
        from PIL import Image
    except ImportError:
        return None

    try:
        img = Image.open(image_path).convert("RGB")
    except (FileNotFoundError, OSError):
        return None

    # Ensure height is even
    if height % 2 != 0:
        height += 1

    img = img.resize((width, height), Image.LANCZOS)
    pixels = img.load()

    lines = []
    for y in range(0, height, 2):
        line = Text()
        for x in range(width):
            top_r, top_g, top_b = pixels[x, y]
            bot_r, bot_g, bot_b = pixels[x, y + 1]
            line.append(
                "▀",
                style=f"rgb({top_r},{top_g},{top_b}) on rgb({bot_r},{bot_g},{bot_b})",
            )
        # Pad to consistent width with trailing space
        line.append("    ")
        lines.append(line)

    return lines
