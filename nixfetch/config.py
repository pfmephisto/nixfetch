"""
Configuration for nixfetch
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json


@dataclass
class NixFetchConfig:
    """Configuration for nixfetch"""
    
    # Analyzers to enable
    enable_metadata: bool = True
    enable_outputs: bool = True
    enable_nixos: bool = True
    enable_stylix: bool = True
    
    # README generation settings
    readme_template: str | None = None
    generate_images: bool = True
    image_format: str = "png"  # png or jpeg
    
    # Display settings
    color_scheme: str = "auto"  # auto, light, dark
    show_errors: bool = True
    
    # Custom sections
    custom_sections: dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, path: Path) -> "NixFetchConfig":
        """Load configuration from JSON file"""
        if not path.exists():
            return cls()
        
        with open(path) as f:
            data = json.load(f)
        
        return cls(**data)
    
    @classmethod
    def from_flake(cls, flake_path: Path) -> "NixFetchConfig":
        """Load configuration from flake directory"""
        config_path = flake_path / "nixfetch.json"
        if config_path.exists():
            return cls.from_file(config_path)
        return cls()
    
    def to_file(self, path: Path) -> None:
        """Save configuration to JSON file"""
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)
