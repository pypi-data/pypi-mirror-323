# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# pylint: disable-msg=invalid-name,redefined-builtin
from os import environ

import argos

project = "Argos monitoring"
copyright = "2023, Alexis Métaireau, Framasoft"
author = "Alexis Métaireau, Framasoft"
release = argos.VERSION

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser", "sphinx_design", "sphinxcontrib.mermaid"]
myst_enable_extensions = ["colon_fence"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
mermaid_params = ["--theme", "forest"]

html_sidebars = {
    "**": [
        "sidebars/localtoc.html",
        "repository.html",
    ]
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

smartquotes = False

if "CI_JOB_ID" in environ:
    html_baseurl = "https://argos-monitoring.framasoft.org"

html_theme = "shibuya"
html_static_path = ["_static"]
html_css_files = ["fonts.css", "fix-nav.css"]
html_logo = "_static/logo.png"
html_theme_options = {
    "og_image_url": "https://argos-monitoring.framasoft.org/_static/logo.png"
}
