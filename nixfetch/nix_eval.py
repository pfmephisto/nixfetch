"""
Evaluate host details (system, users, stylix config) from a flake in a single nix eval call.
"""

import json
import subprocess


NIX_EXPR = r"""
configs: builtins.mapAttrs (name: cfg: {
  system = cfg.config.nixpkgs.system or "unknown";
  users = builtins.mapAttrs (uname: ucfg: {
    stylixEnabled = ucfg.stylix.enable or false;
    polarity = if ucfg.stylix.enable or false then ucfg.stylix.polarity or null else null;
    wallpaper = if ucfg.stylix.enable or false then toString ucfg.stylix.image else null;
    base16Scheme = if ucfg.stylix.enable or false then toString ucfg.stylix.base16Scheme else null;
  }) (cfg.config.home-manager.users or {});
}) configs
""".strip()


def eval_host_details(flake_path: str) -> dict:
    """Evaluate host+user+stylix details for all nixosConfigurations in a flake.

    Returns a dict like:
        {host: {system, users: {user: {stylixEnabled, polarity, wallpaper, base16Scheme}}}}

    Returns {} on any failure (no nixosConfigurations, no HM, eval error, etc.).
    """
    try:
        result = subprocess.run(
            [
                "nix", "eval",
                f"{flake_path}#nixosConfigurations",
                "--apply", NIX_EXPR,
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return {}
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return {}
