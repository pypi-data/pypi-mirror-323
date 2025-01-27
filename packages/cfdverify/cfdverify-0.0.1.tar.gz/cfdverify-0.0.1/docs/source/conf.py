# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = "CFDverify"
copyright = "2025, Oak Ridge National Laboratory"
author = "Justin Weinmeister"
version = "0.0"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
]

# HTML options
html_theme = "sphinx_rtd_theme"
