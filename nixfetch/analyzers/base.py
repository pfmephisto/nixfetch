"""
Base classes for flake analyzers
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AnalyzerResult:
    """Result from an analyzer"""
    analyzer_name: str
    data: dict[str, Any] = field(default_factory=dict)
    images: dict[str, Path] = field(default_factory=dict)  # name -> path to generated image
    errors: list[str] = field(default_factory=list)


class Analyzer(ABC):
    """Base class for flake analyzers"""
    
    def __init__(self, flake_path: Path):
        self.flake_path = flake_path
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of this analyzer"""
        pass
    
    @abstractmethod
    def analyze(self) -> AnalyzerResult:
        """Analyze the flake and return results"""
        pass
    
    def is_applicable(self) -> bool:
        """Check if this analyzer is applicable to the flake"""
        return True
