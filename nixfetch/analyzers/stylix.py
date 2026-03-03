"""
Stylix analyzer for extracting theme information
"""
import json
from pathlib import Path

from ..cmd import run, RunOpts
from ..nix import nix_command
from .base import Analyzer, AnalyzerResult


class StylixAnalyzer(Analyzer):
    """Analyzes stylix configuration for themes and colors"""
    
    @property
    def name(self) -> str:
        return "stylix"
    
    def is_applicable(self) -> bool:
        """Check if flake uses stylix"""
        try:
            from ..nix import nix_metadata
            metadata = nix_metadata(str(self.flake_path))
            inputs = metadata.get("locks", {}).get("nodes", {})
            return "stylix" in inputs
        except Exception:
            return False
    
    def analyze(self) -> AnalyzerResult:
        result = AnalyzerResult(analyzer_name=self.name)
        
        if not self.is_applicable():
            return result
        
        try:
            # Try to extract stylix configuration from NixOS configurations
            from ..nix import nix_flake_show
            show_data = nix_flake_show(str(self.flake_path))
            nixos_configs = show_data.get("nixosConfigurations", {})
            
            themes = {}
            for host_name in nixos_configs.keys():
                theme_info = self._extract_theme(host_name)
                if theme_info:
                    themes[host_name] = theme_info
            
            result.data = {"themes": themes}
        except Exception as e:
            result.errors.append(f"Failed to analyze stylix: {str(e)}")
        
        return result
    
    def _extract_theme(self, host_name: str) -> dict | None:
        """Extract theme information for a host"""
        theme_info = {}
        
        # Try to get base16 scheme
        try:
            cmd = nix_command([
                "eval",
                "--json",
                f"{self.flake_path}#nixosConfigurations.{host_name}.config.stylix.base16Scheme"
            ])
            proc = run(cmd, RunOpts(check=False))
            if proc.returncode == 0:
                scheme = json.loads(proc.stdout)
                if isinstance(scheme, dict):
                    theme_info["colorScheme"] = {
                        "name": scheme.get("scheme", "Unknown"),
                        "author": scheme.get("author", "Unknown"),
                        "colors": {
                            f"base{i:02X}": scheme.get(f"base{i:02X}") 
                            for i in range(16) 
                            if f"base{i:02X}" in scheme
                        }
                    }
        except Exception:
            pass
        
        # Try to get wallpaper
        try:
            cmd = nix_command([
                "eval",
                "--json",
                f"{self.flake_path}#nixosConfigurations.{host_name}.config.stylix.image"
            ])
            proc = run(cmd, RunOpts(check=False))
            if proc.returncode == 0:
                wallpaper = json.loads(proc.stdout)
                if wallpaper and isinstance(wallpaper, str):
                    theme_info["wallpaper"] = wallpaper
        except Exception:
            pass
        
        # Try to get fonts
        try:
            cmd = nix_command([
                "eval",
                "--json",
                f"{self.flake_path}#nixosConfigurations.{host_name}.config.stylix.fonts.sansSerif.name"
            ])
            proc = run(cmd, RunOpts(check=False))
            if proc.returncode == 0:
                font = json.loads(proc.stdout)
                if font:
                    theme_info["font"] = font
        except Exception:
            pass
        
        return theme_info if theme_info else None
