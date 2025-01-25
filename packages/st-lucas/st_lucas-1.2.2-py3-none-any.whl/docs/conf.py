# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# Problems with imports? Could try `export PYTHONPATH=$PYTHONPATH:`pwd`` from root project dir...
import os
import sys
sys.path.insert(0, os.path.abspath('../'))  # Source code dir relative to this file

import st_lucas

# -- Project information -----------------------------------------------------

project = 'ST_LUCAS library'
copyright = '2019-2022, Geo-harmonizer project team; 2023-2024 CTU GeoForAll Lab'
author = 'CTU GeoForAll Lab'

# The short X.Y version
version = '.'.join(st_lucas.__version__.split('.')[:-1])
# The full version, including alpha/beta/rc tags
release = st_lucas.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',  # Core Sphinx library for auto html doc generation from docstrings
    'sphinx.ext.autosummary',  # Create neat summary tables for modules/classes/methods etc
    'sphinx.ext.intersphinx',  # Link to other project's documentation (see mapping below)
    'sphinx.ext.viewcode',  # Add a link to the Python source code for classes, functions etc.
    'sphinx_autodoc_typehints', # Automatically document param types (less noise in class signature)
    'nbsphinx',  # Integrate Jupyter Notebooks and Sphinx
    'sphinx_copybutton',
    'IPython.sphinxext.ipython_console_highlighting'
]

# Mappings for sphinx.ext.intersphinx. Projects have to have Sphinx-generated doc! (.inv file)
intersphinx_mapping = {
#    "python": ("https://docs.python.org/3/", None)
}

autosummary_generate = True  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
html_show_sourcelink = True  # Remove 'view source code' from top of page (for html, not python)
autodoc_inherit_docstrings = True  # If no docstring, inherit from base class
set_type_checking_flag = True  # Enable 'expensive' imports for sphinx_autodoc_typehints
nbsphinx_allow_errors = True  # Continue through Jupyter errors
#autodoc_typehints = "description" # Sphinx-native method. Not as good as sphinx_autodoc_typehints
add_module_names = False # Remove namespaces from class/method signatures

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
html_context = { 'HOSTNAME': os.getenv('HOSTNAME', '') }

# Pydata theme
html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo.png"
html_theme_options = {
    "collapse_navigation" : False,
    "icon_links": [
        {
            "name": "GitLab",
            "url": "https://gitlab.com/geoharmonizer_inea/st_lucas",
            "icon": "fab fa-gitlab",
        }
    ],
    "external_links": [
      {"name": "ST_LUCAS", "url": "https://geoforall.fsv.cvut.cz/st_lucas"},
    ],
    "show_prev_next": False,
    "navbar_end": ["navbar-icon-links.html"],
    "navbar_align": "left",
    "navbar_center": ["major_links"],
    "show_nav_level": 2,
    "footer_start": ["copyright"],
    "footer_center": [],
    "footer_end": [],
}
html_sidebars = {
#    "**": ["sidebar-nav-bs.html", "sidebar-ethical-ads.html"]
    "**": []
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Display todos by setting to True
todo_include_todos = True
