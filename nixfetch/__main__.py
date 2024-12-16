import argparse
import json

from .app import NixFetchApp

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.parse_args()

    metadata = None
    showdata = None

    # Loading some sample data. Later this should be read form the flake using nix flake show and nix flake metadata
    with open('./flake-metadata.json') as f:
        metadata = json.load(f)
    with open('./flake-show.json') as f:
        showdata = json.load(f)

    app = NixFetchApp(metadata, showdata)
    app.display()
