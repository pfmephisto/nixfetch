"""
Neofetch-style terminal display for flake information.
"""

import re
from datetime import datetime

from rich.console import Console
from rich.text import Text

from .ascii_art import NIX_BLUE, NIX_DARK_BLUE, NIX_LOGO_WIDTH, get_colored_logo, get_scheme_colored_logo
from .wallpaper_art import render_wallpaper


def _parse_theme_name(base16_path: str) -> str | None:
    """Extract a theme name from a base16 scheme store path or YAML file.

    Tries the filename first (e.g. '.../nord.yaml' -> 'Nord'),
    then attempts to read the 'name' field from the YAML.
    """
    if not base16_path:
        return None

    # Try filename: /nix/store/...-base16-schemes-.../share/themes/nord.yaml -> nord
    match = re.search(r'/([^/]+?)\.ya?ml$', base16_path)
    if match:
        raw = match.group(1)
        # Convert kebab-case to title case
        return raw.replace("-", " ").replace("_", " ").title()

    # Try reading YAML name field
    try:
        with open(base16_path) as f:
            for line in f:
                if line.startswith("name:"):
                    return line.split(":", 1)[1].strip().strip('"').strip("'")
    except (FileNotFoundError, OSError):
        pass

    return None


def _load_base16_colors(base16_path: str) -> dict | None:
    """Load base16 color values from a YAML scheme file.

    Returns a dict like {'base00': '#191724', 'base01': '#1f1d2e', ...} or None.
    """
    if not base16_path:
        return None
    try:
        colors = {}
        with open(base16_path) as f:
            for line in f:
                line = line.strip()
                match = re.match(r'^(base[0-9A-Fa-f]{2})\s*:\s*["\']?([0-9A-Fa-f]{6})["\']?', line)
                if match:
                    colors[match.group(1)] = "#" + match.group(2)
        return colors if colors else None
    except (FileNotFoundError, OSError):
        return None


class FetchDisplay:

    def __init__(self, metadata: dict, showdata: dict, console: Console,
                 flake_path=None, host_details: dict | None = None):
        self.metadata = metadata
        self.showdata = showdata
        self.console = console
        self.flake_path = flake_path
        self.host_details = host_details or {}

    def render(self):
        info_lines = self._build_info_lines()
        term_width = self.console.width
        narrow = term_width < 70

        if narrow:
            for line in info_lines:
                self.console.print(line)
        else:
            logo_lines = self._get_art()
            art_width = len(logo_lines[0]) if logo_lines else NIX_LOGO_WIDTH
            info_max = max(term_width - art_width, 20)

            total = max(len(logo_lines), len(info_lines))
            blank = Text(" " * art_width)

            for i in range(total):
                art = logo_lines[i] if i < len(logo_lines) else blank
                info = info_lines[i] if i < len(info_lines) else Text("")
                combined = art.copy()
                combined.append(info)
                combined.truncate(term_width)
                self.console.print(combined, overflow="ignore", no_wrap=True)

        self.console.print()
        self.console.print(self._build_color_palette())

        # Host details section
        if self.host_details:
            self.console.print()
            self._render_host_details()

    def _get_art(self) -> list[Text]:
        """Get the left-side art with fallback chain:
        1. First user's wallpaper -> pixel art
        2. First user's base16 scheme -> colored Nix logo
        3. Default Nix blue logo
        """
        first_wallpaper, first_scheme_path = self._find_first_stylix()

        # Try wallpaper pixel art, sized to fit terminal
        if first_wallpaper:
            term_width = self.console.width
            # Reserve at least 30 cols for info; use up to half the terminal for art
            art_width = min(max(term_width // 2, 20), term_width - 30)
            art_height = max(art_width * 9 // 16, 12)  # ~16:9 aspect, at least 12
            # Ensure even height (half-block rendering needs pairs of rows)
            art_height += art_height % 2
            art = render_wallpaper(first_wallpaper, width=art_width, height=art_height)
            if art:
                return art

        # Try scheme-colored logo
        if first_scheme_path:
            colors = _load_base16_colors(first_scheme_path)
            if colors:
                return get_scheme_colored_logo(colors)

        # Default
        return get_colored_logo()

    def _find_first_stylix(self) -> tuple[str | None, str | None]:
        """Find the first non-root user's wallpaper and base16 scheme path."""
        for _host, details in self.host_details.items():
            users = details.get("users", {})
            for uname, ucfg in users.items():
                if uname == "root":
                    continue
                if ucfg.get("stylixEnabled"):
                    wallpaper = ucfg.get("wallpaper")
                    scheme = ucfg.get("base16Scheme")
                    return wallpaper, scheme
        return None, None

    def _label(self, label: str, value: str) -> Text:
        text = Text()
        text.append(label, style=f"bold {NIX_BLUE}")
        text.append(": ", style=f"bold {NIX_BLUE}")
        text.append(value)
        return text

    def _build_info_lines(self) -> list[Text]:
        lines: list[Text] = []

        # Title
        name = self.metadata.get("description", "") or str(
            self.metadata.get("url", "nixfetch")
        )
        title = Text(name, style="bold white")
        lines.append(title)

        # Separator
        lines.append(Text("-" * min(len(name), 40), style="dim"))

        # Description
        desc = self.metadata.get("description")
        if desc:
            lines.append(self._label("Description", desc))

        # URL
        url = self.metadata.get("url")
        if url:
            lines.append(self._label("URL", url))

        # Revision
        rev = self.metadata.get("revision")
        if rev:
            lines.append(self._label("Revision", rev[:8]))

        # Last Modified
        last_modified = self.metadata.get("lastModified")
        if last_modified:
            dt = datetime.fromtimestamp(int(last_modified))
            lines.append(self._label("Last Modified", dt.strftime("%Y-%m-%d")))

        # Inputs
        lock_nodes = self.metadata.get("locks", {}).get("nodes", {})
        input_names = [k for k in lock_nodes if k != "root"]
        if input_names:
            if len(input_names) <= 5:
                names_str = ", ".join(input_names)
            else:
                names_str = ", ".join(input_names[:5]) + ", ..."
            lines.append(
                self._label("Inputs", f"{len(input_names)} ({names_str})")
            )

        # Outputs
        output_categories = [k for k in self.showdata if self.showdata[k]]
        if output_categories:
            lines.append(self._label("Outputs", ", ".join(output_categories)))

        # NixOS Configs
        nixos_configs = self.showdata.get("nixosConfigurations", {})
        if nixos_configs:
            hosts = list(nixos_configs.keys())
            lines.append(self._label("NixOS Configs", ", ".join(hosts)))

        # Packages
        packages = self.showdata.get("packages", {})
        if packages:
            for system, pkgs in packages.items():
                count = len(pkgs) if isinstance(pkgs, (list, dict)) else 0
                lines.append(self._label("Packages", f"{count} ({system})"))

        # DevShells
        devshells = self.showdata.get("devShells", {})
        if devshells:
            for system, shells in devshells.items():
                count = len(shells) if isinstance(shells, (list, dict)) else 0
                lines.append(self._label("DevShells", f"{count} ({system})"))

        return lines

    def _render_host_details(self):
        """Render the host details section below the main fetch."""
        header = Text()
        header.append("  Hosts", style=f"bold {NIX_BLUE}")
        self.console.print(header)

        separator = Text()
        separator.append("  " + "\u2500" * 5, style="dim")
        self.console.print(separator)

        for host, details in self.host_details.items():
            system = details.get("system", "unknown")
            host_line = Text()
            host_line.append(f"  {host}", style="bold white")
            host_line.append(f" \u2014 {system}", style="dim")
            self.console.print(host_line)

            users = details.get("users", {})
            for uname, ucfg in users.items():
                user_line = Text()
                if ucfg.get("stylixEnabled"):
                    theme_name = _parse_theme_name(ucfg.get("base16Scheme", ""))
                    polarity = ucfg.get("polarity", "")
                    parts = []
                    if theme_name:
                        parts.append(theme_name)
                    if polarity:
                        parts.append(f"({polarity})")
                    theme_str = " ".join(parts) if parts else "stylix"
                    user_line.append(f"    {uname}: ", style="dim")
                    user_line.append(theme_str)
                else:
                    user_line.append(f"    {uname}", style="dim")
                self.console.print(user_line)

    def _build_color_palette(self) -> Text:
        """Build Unicode color blocks for ANSI colors 0-7."""
        palette = Text()
        colors = [
            "black", "red", "green", "yellow",
            "blue", "magenta", "cyan", "white",
        ]
        for i, color_name in enumerate(colors):
            palette.append("\u2588\u2588\u2588", style=f"{color_name}")
            if i < len(colors) - 1:
                palette.append(" ")
        return palette
