"""
Outputs analyzer for flake outputs (packages, apps, etc.)
"""
from pathlib import Path

from ..nix import nix_flake_show
from .base import Analyzer, AnalyzerResult


class OutputsAnalyzer(Analyzer):
    """Analyzes flake outputs"""
    
    @property
    def name(self) -> str:
        return "outputs"
    
    def analyze(self) -> AnalyzerResult:
        result = AnalyzerResult(analyzer_name=self.name)
        
        try:
            show_data = nix_flake_show(str(self.flake_path))
            
            result.data = {
                "packages": self._extract_by_category(show_data, "packages"),
                "apps": self._extract_by_category(show_data, "apps"),
                "devShells": self._extract_by_category(show_data, "devShells"),
                "nixosConfigurations": self._extract_nixos_configs(show_data),
                "homeConfigurations": self._extract_by_category(show_data, "homeConfigurations"),
                "templates": self._extract_templates(show_data),
                "overlays": list(show_data.get("overlays", {}).keys()),
                "nixosModules": list(show_data.get("nixosModules", {}).keys()),
                "homeManagerModules": list(show_data.get("homeManagerModules", {}).keys()),
            }
        except Exception as e:
            result.errors.append(f"Failed to get outputs: {str(e)}")
        
        return result
    
    def _extract_by_category(self, data: dict, category: str) -> dict:
        """Extract outputs by category and system"""
        category_data = data.get(category, {})
        systems = {}
        
        for key, value in category_data.items():
            if isinstance(value, dict):
                # System-specific outputs
                for item_key, item_value in value.items():
                    if key not in systems:
                        systems[key] = []
                    if isinstance(item_value, dict) and "type" in item_value:
                        systems[key].append({
                            "name": item_key,
                            "type": item_value.get("type", "unknown"),
                            "description": item_value.get("description", ""),
                        })
        
        return systems
    
    def _extract_nixos_configs(self, data: dict) -> dict:
        """Extract NixOS configuration names"""
        nixos_configs = data.get("nixosConfigurations", {})
        configs = {}
        
        for name, config in nixos_configs.items():
            configs[name] = {
                "type": config.get("type", "nixos-configuration"),
                "description": config.get("description", ""),
            }
        
        return configs
    
    def _extract_templates(self, data: dict) -> dict:
        """Extract templates"""
        templates_data = data.get("templates", {})
        templates = {}
        
        for name, template in templates_data.items():
            templates[name] = {
                "description": template.get("description", ""),
                "path": template.get("path", ""),
            }
        
        return templates
