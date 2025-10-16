"""
Data Whisperer - OSINT Entity Extraction & Mapping Tool

A professional Python-based OSINT tool that extracts entities from unstructured text dumps,
classifies them intelligently, and generates interactive visual network maps.
"""

__version__ = "1.0.0"
__author__ = "Data Whisperer Project"

from .extractor import EntityExtractor
from .classify import EntityClassifier
from .mapbuilder import GraphBuilder
from .visualize import NetworkVisualizer
from .export import ExportManager

__all__ = [
    'EntityExtractor',
    'EntityClassifier',
    'GraphBuilder',
    'NetworkVisualizer',
    'ExportManager'
]

