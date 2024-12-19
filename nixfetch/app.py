"""
An App that displays the nix flake stats
"""
from pathlib import Path

from rich import print
from rich.console import Console, Group
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

from datetime import datetime

from .nix import nix_flake_show, nix_metadata



console = Console()

class NixFetchApp():

    def __init__(self, path=Path):
        self.metadata = nix_metadata(str(path))
        self.showdata = nix_flake_show(str(path))


    def display(self):

        title_text = Text(f"{self.metadata['description']}\nLast modifid:  {datetime.utcfromtimestamp(int(self.metadata['lastModified']))}")

        inputs = Panel('\n'.join(map(str, [f'{k}' for k, v in self.metadata['locks']['nodes'].items()])) , title="Inputs")
        outputs = Panel('\n'.join(map(str, [f'{k}' for k, v in self.showdata.items()])), title="Outputs")
        columns = Columns([inputs, outputs])
        console.print(title_text)
        console.print(columns)
