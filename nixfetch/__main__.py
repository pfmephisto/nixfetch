import argparse
import json
from pathlib import Path

from .app import NixFetchApp

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('path',
                        help="The path to the flake",
                        type=Path)

    args = parser.parse_args()

    app = NixFetchApp(args.path)
    app.display()

if __name__ == "__main__":
    run()

