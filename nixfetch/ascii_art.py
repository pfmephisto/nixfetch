"""
Nix snowflake ASCII art for neofetch-style display.
"""

from rich.text import Text

NIX_BLUE = "#7EBAE4"
NIX_DARK_BLUE = "#5277C3"

NIX_LOGO = [
    r"    \\  \\ //  //   ",
    r"     \\  \\//  //   ",
    r"      \\  \\  //    ",
    r" ///\\\\  \\//      ",
    r"///  \\\\  \\       ",
    r"//    \\  \\  \\    ",
    r"       //  \\  \\   ",
    r"      //  //\\  \\  ",
    r"     //  //  \\  \\ ",
    r"    //  //    \\  \\",
    r"   \\  \\  //\\\\  ",
    r"    \\  \\//  \\\\  ",
]

NIX_LOGO_WIDTH = max(len(line) for line in NIX_LOGO) + 4


def get_colored_logo() -> list[Text]:
    """Returns logo lines colored in Nix blue using Rich Text objects."""
    lines = []
    for line in NIX_LOGO:
        text = Text(line.ljust(NIX_LOGO_WIDTH))
        text.stylize(f"bold {NIX_DARK_BLUE}")
        lines.append(text)
    return lines


def get_scheme_colored_logo(base16_colors: dict) -> list[Text]:
    """Returns logo lines colored using base16 scheme accent colors.

    Uses base0C, base0D, base0E for a tri-color effect on the logo.
    Falls back to default Nix blue if colors are missing.
    """
    accent1 = base16_colors.get("base0D", NIX_DARK_BLUE)
    accent2 = base16_colors.get("base0E", NIX_DARK_BLUE)
    accent3 = base16_colors.get("base0C", NIX_DARK_BLUE)

    # Ensure colors have # prefix
    for color in [accent1, accent2, accent3]:
        if not color.startswith("#"):
            color = "#" + color

    accents = [accent1, accent2, accent3]

    lines = []
    for i, line in enumerate(NIX_LOGO):
        text = Text(line.ljust(NIX_LOGO_WIDTH))
        color = accents[i % len(accents)]
        if not color.startswith("#"):
            color = "#" + color
        text.stylize(f"bold {color}")
        lines.append(text)
    return lines
