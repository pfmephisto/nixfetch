import argparse
from pathlib import Path

from .app import NixFetchApp, AppMode


def run():
    parser = argparse.ArgumentParser(
        description="nixfetch - A fastfetch-like tool for Nix flakes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nixfetch /path/to/flake              # Display flake info
  nixfetch /path/to/flake --analyze    # Show detailed analysis
  nixfetch /path/to/flake --readme     # Generate README.md
  nixfetch /path/to/flake --readme -o /path/to/output/README.md
        """
    )
    
    parser.add_argument(
        'path',
        help="The path to the flake",
        type=Path,
        nargs='?',
        default=Path.cwd()
    )
    
    parser.add_argument(
        '--analyze',
        help="Run detailed analysis and display results",
        action='store_true'
    )
    
    parser.add_argument(
        '--readme',
        help="Generate a README.md file from flake analysis",
        action='store_true'
    )
    
    parser.add_argument(
        '-o', '--output',
        help="Output path for README (default: README.md in flake directory)",
        type=Path,
        default=None
    )

    args = parser.parse_args()
    
    # Determine mode
    if args.readme:
        mode = AppMode.README
    elif args.analyze:
        mode = AppMode.ANALYZE
    else:
        mode = AppMode.DISPLAY

    app = NixFetchApp(args.path, mode=mode)
    
    if mode == AppMode.README:
        app.generate_readme(args.output)
    else:
        app.run()


if __name__ == "__main__":
    run()

