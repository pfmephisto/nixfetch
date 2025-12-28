"""
NixOS configuration analyzer
"""
import json
from pathlib import Path

from ..cmd import run, RunOpts
from ..nix import nix_command
from .base import Analyzer, AnalyzerResult


class NixOSAnalyzer(Analyzer):
    """Analyzes NixOS configurations in the flake"""
    
    @property
    def name(self) -> str:
        return "nixos"
    
    def is_applicable(self) -> bool:
        """Check if flake has NixOS configurations"""
        try:
            from ..nix import nix_flake_show
            show_data = nix_flake_show(str(self.flake_path))
            return "nixosConfigurations" in show_data and len(show_data["nixosConfigurations"]) > 0
        except:
            return False
    
    def analyze(self) -> AnalyzerResult:
        result = AnalyzerResult(analyzer_name=self.name)
        
        if not self.is_applicable():
            return result
        
        try:
            from ..nix import nix_flake_show
            show_data = nix_flake_show(str(self.flake_path))
            nixos_configs = show_data.get("nixosConfigurations", {})
            
            hosts = {}
            for host_name in nixos_configs.keys():
                host_info = self._analyze_host(host_name)
                if host_info:
                    hosts[host_name] = host_info
            
            result.data = {"hosts": hosts}
        except Exception as e:
            result.errors.append(f"Failed to analyze NixOS configurations: {str(e)}")
        
        return result
    
    def _analyze_host(self, host_name: str) -> dict | None:
        """Analyze a specific host configuration"""
        host_info = {
            "name": host_name,
            "system": None,
            "modules": [],
            "features": [],
        }
        
        try:
            # Try to evaluate host system
            cmd = nix_command([
                "eval",
                "--json",
                f"{self.flake_path}#nixosConfigurations.{host_name}.config.nixpkgs.system"
            ])
            proc = run(cmd, RunOpts(check=False))
            if proc.returncode == 0:
                host_info["system"] = json.loads(proc.stdout)
        except:
            pass
        
        try:
            # Try to get hostname
            cmd = nix_command([
                "eval",
                "--json",
                f"{self.flake_path}#nixosConfigurations.{host_name}.config.networking.hostName"
            ])
            proc = run(cmd, RunOpts(check=False))
            if proc.returncode == 0:
                host_info["hostname"] = json.loads(proc.stdout)
        except:
            pass
        
        return host_info
