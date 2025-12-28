"""
Metadata analyzer for flake metadata
"""
import json
from datetime import datetime
from pathlib import Path

from ..nix import nix_metadata
from .base import Analyzer, AnalyzerResult


class MetadataAnalyzer(Analyzer):
    """Analyzes flake metadata"""
    
    @property
    def name(self) -> str:
        return "metadata"
    
    def analyze(self) -> AnalyzerResult:
        result = AnalyzerResult(analyzer_name=self.name)
        
        try:
            metadata = nix_metadata(str(self.flake_path))
            
            # Extract key information
            result.data = {
                "description": metadata.get("description", "No description"),
                "url": metadata.get("url", ""),
                "original_url": metadata.get("originalUrl", ""),
                "last_modified": datetime.utcfromtimestamp(
                    int(metadata.get("lastModified", 0))
                ).isoformat() if metadata.get("lastModified") else None,
                "revision": metadata.get("revision", "")[:8] if metadata.get("revision") else None,
                "inputs": self._extract_inputs(metadata),
                "locked": metadata.get("locked", False),
            }
        except Exception as e:
            result.errors.append(f"Failed to get metadata: {str(e)}")
        
        return result
    
    def _extract_inputs(self, metadata: dict) -> dict[str, dict]:
        """Extract input information from metadata"""
        inputs = {}
        locks = metadata.get("locks", {}).get("nodes", {})
        
        for name, node in locks.items():
            if name == "root":
                continue
            
            input_info = {
                "type": node.get("locked", {}).get("type", "unknown"),
            }
            
            locked = node.get("locked", {})
            if locked.get("type") == "github":
                input_info["owner"] = locked.get("owner")
                input_info["repo"] = locked.get("repo")
                input_info["ref"] = locked.get("ref")
                input_info["rev"] = locked.get("rev", "")[:8]
            elif locked.get("type") == "path":
                input_info["path"] = locked.get("path")
            
            inputs[name] = input_info
        
        return inputs
