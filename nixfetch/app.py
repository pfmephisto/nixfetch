"""
An App that displays the nix flake stats
"""
from rich import print
from rich.console import Console, Group
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

from datetime import datetime

console = Console()

class NixFetchApp():

    def __init__(self, metadata, showdata):
        self.metadata = metadata
        self.showdata = showdata


    def display(self):
        #print(self.metadata)
        #print(self.showdata)

        title_text = Text(f"{self.metadata['description']}\nLast modifid:  {datetime.utcfromtimestamp(int(self.metadata['lastModified']))}")

        #print(self.metadata['locks']['nodes'])

        inputs = Panel('\n'.join(map(str, [f'{k}' for k, v in self.metadata['locks']['nodes'].items()])) , title="Inputs")
        outputs = Panel('\n'.join(map(str, [f'{k}' for k, v in self.showdata.items()])), title="Outputs")
        columns = Columns([inputs, outputs])
        console.print(title_text)
        console.print(columns)
