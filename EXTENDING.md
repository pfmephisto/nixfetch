# Extending nixfetch

This guide explains how to extend nixfetch with custom analyzers and generators.

## Creating a Custom Analyzer

Analyzers extract information from Nix flakes. To create a custom analyzer:

### 1. Create the Analyzer Class

Create a new file in `nixfetch/analyzers/`, e.g., `custom.py`:

```python
"""
Custom analyzer for extracting specific information
"""
from pathlib import Path
from ..cmd import run, RunOpts
from ..nix import nix_command
from .base import Analyzer, AnalyzerResult


class CustomAnalyzer(Analyzer):
    """Analyzes custom aspects of the flake"""
    
    @property
    def name(self) -> str:
        return "custom"
    
    def is_applicable(self) -> bool:
        """Check if this analyzer should run"""
        # Return True to always run, or add custom logic
        return True
    
    def analyze(self) -> AnalyzerResult:
        result = AnalyzerResult(analyzer_name=self.name)
        
        try:
            # Use nix commands to extract information
            cmd = nix_command([
                "eval",
                "--json",
                f"{self.flake_path}#customAttribute"
            ])
            proc = run(cmd, RunOpts(check=False))
            
            if proc.returncode == 0:
                import json
                data = json.loads(proc.stdout)
                result.data = {"customData": data}
        except Exception as e:
            result.errors.append(f"Failed to analyze: {str(e)}")
        
        return result
```

### 2. Register the Analyzer

Add your analyzer to `nixfetch/analyzers/__init__.py`:

```python
from .custom import CustomAnalyzer

__all__ = [
    # ... existing analyzers
    "CustomAnalyzer",
]
```

### 3. Use the Analyzer

Add it to `app.py` in the `__init__` method:

```python
from .analyzers import (
    # ... existing imports
    CustomAnalyzer,
)

# In NixFetchApp.__init__:
if self.config.enable_custom:  # Add to config.py
    self.analyzers.append(CustomAnalyzer(path))
```

## Extending the README Generator

To customize README generation, modify `nixfetch/generators/readme.py`:

### Adding a New Section

```python
def _generate_custom_section(self, result: AnalyzerResult) -> str:
    """Generate custom section"""
    data = result.data.get("customData", {})
    if not data:
        return ""
    
    lines = ["## 🎯 Custom Section\n"]
    lines.append(f"Data: {data}")
    
    return "\n".join(lines)
```

Then add it to the `generate` method:

```python
def generate(self, results: dict[str, AnalyzerResult]) -> str:
    sections = []
    # ... existing sections
    
    if "custom" in results:
        sections.append(self._generate_custom_section(results["custom"]))
    
    return "\n\n".join(sections)
```

## Creating Custom Image Generators

To add new image generation capabilities, extend `ImageGenerator`:

```python
from pathlib import Path
from .images import ImageGenerator


class CustomImageGenerator(ImageGenerator):
    """Generates custom visualization images"""
    
    def generate(self, data: dict, name: str = "custom") -> Path | None:
        """Generate a custom image"""
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            return None
        
        # Create your custom image
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw something
        draw.rectangle([10, 10, 790, 590], outline='black')
        
        output_path = self.output_dir / f"{name}.png"
        img.save(output_path)
        return output_path
```

## Configuration Options

Add custom configuration options in `nixfetch/config.py`:

```python
@dataclass
class NixFetchConfig:
    # ... existing fields
    
    # Your custom options
    enable_custom: bool = True
    custom_option: str = "default_value"
```

## Example: Flake-parts Analyzer

Here's a complete example of an analyzer for flake-parts:

```python
"""
Flake-parts analyzer
"""
from pathlib import Path
from ..nix import nix_eval
from .base import Analyzer, AnalyzerResult


class FlakePartsAnalyzer(Analyzer):
    """Analyzes flake-parts structure"""
    
    @property
    def name(self) -> str:
        return "flake-parts"
    
    def is_applicable(self) -> bool:
        """Check if flake uses flake-parts"""
        try:
            from ..nix import nix_metadata
            metadata = nix_metadata(str(self.flake_path))
            inputs = metadata.get("locks", {}).get("nodes", {})
            return "flake-parts" in inputs
        except:
            return False
    
    def analyze(self) -> AnalyzerResult:
        result = AnalyzerResult(analyzer_name=self.name)
        
        if not self.is_applicable():
            return result
        
        try:
            # Analyze flake-parts modules
            result.data = {
                "uses_flake_parts": True,
                "modules": []  # Extract module information
            }
        except Exception as e:
            result.errors.append(f"Failed to analyze flake-parts: {str(e)}")
        
        return result
```

## Tips

1. **Error Handling**: Always use try-except blocks and add errors to `result.errors`
2. **Performance**: Use `is_applicable()` to skip expensive operations when not needed
3. **Testing**: Test your analyzer with different flake structures
4. **Documentation**: Add docstrings and comments to explain your analyzer's purpose
5. **Nix Commands**: Use `RunOpts(check=False)` to prevent exceptions from failed nix commands

## Contributing

When contributing new analyzers:

1. Follow the existing code style
2. Add tests if possible
3. Update documentation
4. Add examples to EXAMPLE_README.md
5. Submit a pull request with a clear description
