# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))
from fsl_pipe import __version__


# -- Project information -----------------------------------------------------

project = 'fsl-pipe'
author = 'Michiel Cottaar'
version = __version__

# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.imgmath",
    "sphinx.ext.viewcode",
    "sphinx_multiversion",
    "myst_parser",
]

autodoc_member_order = 'bysource'
autodoc_default_options = {
    'special-members': '__init__, __call__',
}

# Options for multi-versioning
smv_branch_whitelist = r"^.*$"
smv_tag_whitelist = r"^.*$"
smv_released_pattern = r'^refs/tags/v1.*$'
smv_latest_version = "v" + release
print("Stable version = ", smv_latest_version)

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'default'
html_theme_options = {
    "stickysidebar": "true",
}
html_sidebars = {
    "**": [
        "localtoc.html",
        "relations.html",
        "sourcelink.html",
        "searchbox.html",
        "versioning.html",
    ],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []