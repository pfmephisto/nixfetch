"""
An App that displays the nix flake stats
"""
from pathlib import Path

from rich import print
from rich.console import Console, Group
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown

from datetime import datetime

from .nix import nix_flake_show, nix_metadata
from .analyzers import (
    MetadataAnalyzer,
    OutputsAnalyzer,
    NixOSAnalyzer,
    StylixAnalyzer,
)
from .generators import ReadmeGenerator, ColorPaletteGenerator
from .config import NixFetchConfig


console = Console()


class NixFetchApp:

    def __init__(self, path: Path, mode: str = "display", config: NixFetchConfig | None = None):
        self.path = path
        self.mode = mode
        self.config = config or NixFetchConfig.from_flake(path)
        self.metadata = nix_metadata(str(path))
        self.showdata = nix_flake_show(str(path))
        
        # Initialize analyzers based on config
        self.analyzers = []
        if self.config.enable_metadata:
            self.analyzers.append(MetadataAnalyzer(path))
        if self.config.enable_outputs:
            self.analyzers.append(OutputsAnalyzer(path))
        if self.config.enable_nixos:
            self.analyzers.append(NixOSAnalyzer(path))
        if self.config.enable_stylix:
            self.analyzers.append(StylixAnalyzer(path))

    def run(self):
        """Run the app in the configured mode"""
        if self.mode == "display":
            self.display()
        elif self.mode == "readme":
            self.generate_readme()
        elif self.mode == "analyze":
            self.analyze_and_display()
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

    def display(self):
        """Display flake info in terminal (original behavior)"""
        description = self.metadata.get('description', 'No description')
        last_modified = self.metadata.get('lastModified')
        
        if last_modified:
            last_mod_str = datetime.utcfromtimestamp(int(last_modified)).isoformat()
        else:
            last_mod_str = 'Unknown'
        
        title_text = Text(
            f"{description}\n"
            f"Last modified: {last_mod_str}"
        )

        locks_nodes = self.metadata.get('locks', {}).get('nodes', {})
        inputs = Panel(
            '\n'.join(map(str, [f'{k}' for k, v in locks_nodes.items()])),
            title="Inputs"
        )
        outputs = Panel(
            '\n'.join(map(str, [f'{k}' for k, v in self.showdata.items()])),
            title="Outputs"
        )
        columns = Columns([inputs, outputs])
        console.print(title_text)
        console.print(columns)

    def analyze_and_display(self):
        """Run analyzers and display detailed results"""
        console.print("[bold cyan]Analyzing flake...[/bold cyan]\n")
        
        results = {}
        for analyzer in self.analyzers:
            if analyzer.is_applicable():
                console.print(f"[dim]Running {analyzer.name} analyzer...[/dim]")
                result = analyzer.analyze()
                results[analyzer.name] = result
                
                if result.errors and self.config.show_errors:
                    for error in result.errors:
                        console.print(f"[yellow]Warning: {error}[/yellow]")
        
        console.print("\n[bold green]✓ Analysis complete![/bold green]\n")
        
        # Display results
        self._display_results(results)

    def _display_results(self, results: dict):
        """Display analysis results in a nice format"""
        # Metadata
        if "metadata" in results:
            self._display_metadata(results["metadata"])
        
        # Outputs
        if "outputs" in results:
            self._display_outputs(results["outputs"])
        
        # NixOS hosts
        if "nixos" in results and results["nixos"].data.get("hosts"):
            self._display_nixos(results["nixos"])
        
        # Stylix themes
        if "stylix" in results and results["stylix"].data.get("themes"):
            self._display_stylix(results["stylix"])

    def _display_metadata(self, result):
        """Display metadata analysis"""
        data = result.data
        
        panel_content = []
        panel_content.append(f"[bold]Description:[/bold] {data.get('description', 'N/A')}")
        panel_content.append(f"[bold]URL:[/bold] {data.get('url', 'N/A')}")
        panel_content.append(f"[bold]Last Modified:[/bold] {data.get('last_modified', 'N/A')}")
        panel_content.append(f"[bold]Revision:[/bold] {data.get('revision', 'N/A')}")
        
        console.print(Panel("\n".join(panel_content), title="📋 Metadata", border_style="cyan"))
        
        # Inputs table
        if data.get("inputs"):
            table = Table(title="Inputs", border_style="blue")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Details", style="green")
            
            for name, info in data["inputs"].items():
                details = []
                if info.get("owner") and info.get("repo"):
                    details.append(f"{info['owner']}/{info['repo']}")
                if info.get("rev"):
                    details.append(f"rev: {info['rev']}")
                table.add_row(name, info.get("type", "unknown"), " ".join(details))
            
            console.print(table)
            console.print()

    def _display_outputs(self, result):
        """Display outputs analysis"""
        data = result.data
        
        # Packages
        if data.get("packages"):
            table = Table(title="📦 Packages", border_style="green")
            table.add_column("System", style="cyan")
            table.add_column("Package", style="green")
            
            for system, pkgs in data["packages"].items():
                for pkg in pkgs:
                    table.add_row(system, pkg.get("name", "unknown"))
            
            console.print(table)
            console.print()
        
        # NixOS configurations
        if data.get("nixosConfigurations"):
            configs = data["nixosConfigurations"]
            console.print(
                Panel(
                    "\n".join([f"• {name}" for name in configs.keys()]),
                    title="🖥️  NixOS Configurations",
                    border_style="yellow"
                )
            )
            console.print()

    def _display_nixos(self, result):
        """Display NixOS hosts"""
        hosts = result.data.get("hosts", {})
        
        table = Table(title="🖥️  NixOS Hosts", border_style="yellow")
        table.add_column("Host", style="cyan")
        table.add_column("System", style="magenta")
        table.add_column("Hostname", style="green")
        
        for name, info in hosts.items():
            table.add_row(
                name,
                info.get("system", "unknown"),
                info.get("hostname", name)
            )
        
        console.print(table)
        console.print()

    def _display_stylix(self, result):
        """Display stylix themes"""
        themes = result.data.get("themes", {})
        
        for host, theme in themes.items():
            panel_content = []
            
            if "colorScheme" in theme:
                scheme = theme["colorScheme"]
                panel_content.append(f"[bold]Scheme:[/bold] {scheme.get('name', 'Unknown')}")
                panel_content.append(f"[bold]Author:[/bold] {scheme.get('author', 'Unknown')}")
            
            if "wallpaper" in theme:
                panel_content.append(f"[bold]Wallpaper:[/bold] {theme['wallpaper']}")
            
            if "font" in theme:
                panel_content.append(f"[bold]Font:[/bold] {theme['font']}")
            
            if panel_content:
                console.print(
                    Panel(
                        "\n".join(panel_content),
                        title=f"🎨 Theme: {host}",
                        border_style="magenta"
                    )
                )
        console.print()

    def generate_readme(self, output_path: Path | None = None):
        """Generate README file from analysis"""
        console.print("[bold cyan]Generating README...[/bold cyan]\n")
        
        # Run all analyzers
        results = {}
        for analyzer in self.analyzers:
            if analyzer.is_applicable():
                console.print(f"[dim]Running {analyzer.name} analyzer...[/dim]")
                result = analyzer.analyze()
                results[analyzer.name] = result
                
                if result.errors and self.config.show_errors:
                    for error in result.errors:
                        console.print(f"[yellow]Warning: {error}[/yellow]")
        
        # Generate images if stylix data is available and enabled
        if self.config.generate_images and "stylix" in results and results["stylix"].data.get("themes"):
            self._generate_theme_images(results["stylix"], output_path)
        
        # Generate README
        generator = ReadmeGenerator(output_path)
        content = generator.generate(results)
        
        # Add custom sections from config
        if self.config.custom_sections:
            custom_content = "\n\n".join(self.config.custom_sections.values())
            content = content + "\n\n" + custom_content
        
        generator.save(content)
        
        console.print(f"\n[bold green]✓ README generated: {generator.output_path}[/bold green]")
        
        # Preview the README
        console.print("\n[bold]Preview:[/bold]\n")
        console.print(Markdown(content[:1000] + "\n..." if len(content) > 1000 else content))

    def _generate_theme_images(self, stylix_result, output_path: Path | None):
        """Generate theme visualization images"""
        themes = stylix_result.data.get("themes", {})
        
        # Determine output directory
        if output_path:
            image_dir = output_path.parent / "assets"
        else:
            image_dir = self.path / "assets"
        
        image_generator = ColorPaletteGenerator(image_dir)
        
        for host, theme in themes.items():
            if "colorScheme" in theme:
                colors = theme["colorScheme"].get("colors", {})
                if colors:
                    console.print(f"[dim]Generating color palette for {host}...[/dim]")
                    image_path = image_generator.generate(colors, f"palette_{host}")
                    if image_path:
                        console.print(f"[dim]  → {image_path}[/dim]")
