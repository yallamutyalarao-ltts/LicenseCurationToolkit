"""
ConanX - Conan 2.0 Package CLI

A comprehensive command-line interface tool for automating Conan 2.0 package
creation, upload, download, and management operations with integrated Artifactory support.
"""

__version__ = "1.0.0"
__author__ = "Arkajyoti"

from conanx.cli import main

__all__ = ["main", "__version__"]
