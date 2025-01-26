"""Sphinx configuration for lifecyclelogging documentation."""

from __future__ import annotations


# Project information
project = "lifecyclelogging"
project_copyright = "2024, Jon Bogaty"
author = "Jon Bogaty"

# The full version, including alpha/beta/rc tags
version = "0.1.0"
release = version

# Extensions
extensions = [
    "autodoc2",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
]

# Autodoc2 settings
autodoc2_packages = [
    {
        "path": "../src/lifecyclelogging",
        "auto_mode": True,
    }
]

autodoc2_docstring_parser = "google"  # Use Google style docstrings

# List of patterns to exclude from document discovery
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The theme to use for HTML and Help pages
html_theme = "sphinx_rtd_theme"
