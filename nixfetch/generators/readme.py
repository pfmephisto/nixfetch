"""
README generator for Nix flakes
"""
from pathlib import Path
from typing import Any

from ..analyzers import AnalyzerResult


class ReadmeGenerator:
    """Generates a README.md file from analysis results"""
    
    def __init__(self, output_path: Path | None = None):
        self.output_path = output_path or Path("README.md")
    
    def generate(self, results: dict[str, AnalyzerResult]) -> str:
        """Generate README content from analysis results"""
        sections = []
        
        # Add header
        sections.append(self._generate_header(results))
        
        # Add metadata section
        if "metadata" in results:
            sections.append(self._generate_metadata_section(results["metadata"]))
        
        # Add outputs section
        if "outputs" in results:
            sections.append(self._generate_outputs_section(results["outputs"]))
        
        # Add NixOS hosts section
        if "nixos" in results and results["nixos"].data.get("hosts"):
            sections.append(self._generate_nixos_section(results["nixos"]))
        
        # Add stylix theme section
        if "stylix" in results and results["stylix"].data.get("themes"):
            sections.append(self._generate_stylix_section(results["stylix"]))
        
        # Join all sections
        content = "\n\n".join(sections)
        
        return content
    
    def _generate_header(self, results: dict[str, AnalyzerResult]) -> str:
        """Generate README header"""
        metadata = results.get("metadata")
        if metadata and metadata.data:
            title = metadata.data.get("description", "Nix Flake")
            return f"# {title}\n"
        return "# Nix Flake\n"
    
    def _generate_metadata_section(self, result: AnalyzerResult) -> str:
        """Generate metadata section"""
        data = result.data
        lines = ["## 📋 Overview\n"]
        
        if data.get("description"):
            lines.append(f"**Description:** {data['description']}\n")
        
        if data.get("url"):
            lines.append(f"**URL:** `{data['url']}`\n")
        
        if data.get("last_modified"):
            lines.append(f"**Last Modified:** {data['last_modified']}\n")
        
        if data.get("revision"):
            lines.append(f"**Revision:** `{data['revision']}`\n")
        
        # Add inputs table
        if data.get("inputs"):
            lines.append("\n### Inputs\n")
            lines.append("| Input | Type | Details |")
            lines.append("|-------|------|---------|")
            
            for name, info in data["inputs"].items():
                input_type = info.get("type", "unknown")
                details = []
                
                if info.get("owner") and info.get("repo"):
                    details.append(f"{info['owner']}/{info['repo']}")
                if info.get("rev"):
                    details.append(f"rev: `{info['rev']}`")
                if info.get("path"):
                    details.append(f"path: `{info['path']}`")
                
                details_str = ", ".join(details) if details else "-"
                lines.append(f"| `{name}` | {input_type} | {details_str} |")
        
        return "\n".join(lines)
    
    def _generate_outputs_section(self, result: AnalyzerResult) -> str:
        """Generate outputs section"""
        data = result.data
        lines = ["## 📦 Outputs\n"]
        
        # Packages
        packages = data.get("packages", {})
        if packages:
            lines.append("### Packages\n")
            for system, pkgs in packages.items():
                if pkgs:
                    lines.append(f"**{system}:**")
                    for pkg in pkgs:
                        name = pkg.get("name", "unknown")
                        desc = pkg.get("description", "")
                        if desc:
                            lines.append(f"- `{name}` - {desc}")
                        else:
                            lines.append(f"- `{name}`")
                    lines.append("")
        
        # Apps
        apps = data.get("apps", {})
        if apps:
            lines.append("### Applications\n")
            for system, app_list in apps.items():
                if app_list:
                    lines.append(f"**{system}:**")
                    for app in app_list:
                        name = app.get("name", "unknown")
                        lines.append(f"- `{name}`")
                    lines.append("")
        
        # Dev Shells
        dev_shells = data.get("devShells", {})
        if dev_shells:
            lines.append("### Development Shells\n")
            for system, shells in dev_shells.items():
                if shells:
                    lines.append(f"**{system}:** {', '.join(f'`{s.get('name')}`' for s in shells)}")
        
        # NixOS Configurations
        nixos_configs = data.get("nixosConfigurations", {})
        if nixos_configs:
            lines.append("\n### NixOS Configurations\n")
            for name, config in nixos_configs.items():
                desc = config.get("description", "")
                if desc:
                    lines.append(f"- **{name}** - {desc}")
                else:
                    lines.append(f"- **{name}**")
        
        # Templates
        templates = data.get("templates", {})
        if templates:
            lines.append("\n### Templates\n")
            for name, template in templates.items():
                desc = template.get("description", "")
                if desc:
                    lines.append(f"- `{name}` - {desc}")
                else:
                    lines.append(f"- `{name}`")
        
        # Modules
        nixos_modules = data.get("nixosModules", [])
        if nixos_modules:
            lines.append("\n### NixOS Modules\n")
            lines.append(", ".join(f"`{m}`" for m in nixos_modules))
        
        hm_modules = data.get("homeManagerModules", [])
        if hm_modules:
            lines.append("\n### Home Manager Modules\n")
            lines.append(", ".join(f"`{m}`" for m in hm_modules))
        
        # Overlays
        overlays = data.get("overlays", [])
        if overlays:
            lines.append("\n### Overlays\n")
            lines.append(", ".join(f"`{o}`" for o in overlays))
        
        return "\n".join(lines)
    
    def _generate_nixos_section(self, result: AnalyzerResult) -> str:
        """Generate NixOS hosts section"""
        hosts = result.data.get("hosts", {})
        if not hosts:
            return ""
        
        lines = ["## 🖥️ NixOS Hosts\n"]
        lines.append("| Host | System | Hostname |")
        lines.append("|------|--------|----------|")
        
        for name, info in hosts.items():
            system = info.get("system", "unknown")
            hostname = info.get("hostname", name)
            lines.append(f"| **{name}** | `{system}` | `{hostname}` |")
        
        return "\n".join(lines)
    
    def _generate_stylix_section(self, result: AnalyzerResult) -> str:
        """Generate stylix theme section"""
        themes = result.data.get("themes", {})
        if not themes:
            return ""
        
        lines = ["## 🎨 Theming (Stylix)\n"]
        
        for host, theme in themes.items():
            lines.append(f"### {host}\n")
            
            if "colorScheme" in theme:
                scheme = theme["colorScheme"]
                lines.append(f"**Color Scheme:** {scheme.get('name', 'Unknown')}")
                if scheme.get("author"):
                    lines.append(f" by {scheme['author']}")
                lines.append("\n")
                
                # Add color palette
                colors = scheme.get("colors", {})
                if colors:
                    lines.append("**Color Palette:**\n")
                    lines.append("```")
                    for color_name, color_value in sorted(colors.items()):
                        lines.append(f"{color_name}: #{color_value}")
                    lines.append("```\n")
            
            if "wallpaper" in theme:
                wallpaper = theme["wallpaper"]
                lines.append(f"**Wallpaper:** `{wallpaper}`\n")
            
            if "font" in theme:
                font = theme["font"]
                lines.append(f"**Font:** {font}\n")
        
        return "\n".join(lines)
    
    def save(self, content: str) -> None:
        """Save README content to file"""
        self.output_path.write_text(content)
