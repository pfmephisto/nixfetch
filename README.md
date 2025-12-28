# nixfetch

A **fastfetch**-like tool for Nix flakes that analyzes flakes and generates beautiful, comprehensive documentation.

## 🎯 Features

- **📊 Flake Analysis**: Extracts detailed information about flake inputs, outputs, and configurations
- **🖥️ NixOS Host Detection**: Discovers and analyzes NixOS configurations
- **🎨 Stylix Integration**: Extracts color schemes, wallpapers, and fonts from stylix configurations
- **📝 README Generation**: Automatically generates comprehensive README files with:
  - Flake metadata and inputs
  - Available packages, apps, and dev shells
  - NixOS configurations and hosts
  - Theme information with color palettes
  - Custom sections support
- **🎨 Image Generation**: Creates visual representations of color schemes
- **⚙️ Extensible Architecture**: Modular analyzer system for easy customization

## 🚀 Installation

### Using Nix Flakes

```bash
nix run github:pfmephisto/nixfetch -- /path/to/your/flake
```

### From Source

```bash
git clone https://github.com/pfmephisto/nixfetch
cd nixfetch
nix develop
poetry install
```

## 📖 Usage

### Display Flake Info (Default)

Show a quick overview of your flake:

```bash
nixfetch /path/to/flake
```

### Detailed Analysis

Run all analyzers and display comprehensive results:

```bash
nixfetch /path/to/flake --analyze
```

### Generate README

Create a beautiful README.md for your flake:

```bash
# Generate in flake directory
nixfetch /path/to/flake --readme

# Specify output location
nixfetch /path/to/flake --readme -o /path/to/output/README.md
```

## 🔧 Configuration

Create a `nixfetch.json` in your flake directory to customize behavior:

```json
{
  "enable_metadata": true,
  "enable_outputs": true,
  "enable_nixos": true,
  "enable_stylix": true,
  "generate_images": true,
  "image_format": "png",
  "show_errors": true,
  "custom_sections": {
    "contributing": "## Contributing\n\nContributions welcome!",
    "license": "## License\n\nMIT License"
  }
}
```

## 🧩 Analyzers

nixfetch uses a modular analyzer system:

- **MetadataAnalyzer**: Extracts flake metadata, description, revision, and inputs
- **OutputsAnalyzer**: Discovers packages, apps, devShells, templates, and modules
- **NixOSAnalyzer**: Analyzes NixOS configurations and host information
- **StylixAnalyzer**: Extracts theming information from stylix configurations

## 🎨 Image Generation

When stylix is detected, nixfetch can generate:

- Color palette visualizations showing all base16 colors
- Images are saved in the `assets/` directory
- Requires Pillow (install with `poetry install --extras images`)

## 🛠️ Development

This project is extensible by design. To add a new analyzer:

1. Create a new analyzer class inheriting from `Analyzer` in `nixfetch/analyzers/`
2. Implement the `name` property and `analyze()` method
3. Optionally override `is_applicable()` to conditionally enable the analyzer
4. Register it in `nixfetch/analyzers/__init__.py`

## 📋 Examples

### Analyze the nixfetch flake itself

```bash
nixfetch . --analyze
```

### Generate README for your NixOS config

```bash
nixfetch ~/nixos-config --readme -o ~/nixos-config/README.md
```

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Add new analyzers for different flake patterns
- Improve README templates
- Add more image generation capabilities
- Enhance existing analyzers

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Inspired by [fastfetch](https://github.com/fastfetch-cli/fastfetch) and the Nix community.
