import sys
import os
import datetime
from importlib import metadata

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

sys.path.insert(0, os.path.abspath('../..'))

package_data = metadata.metadata("siriuspy")
year = datetime.date.today().year
project = package_data["Name"]
author = package_data["Author"]
copyright = f'{year}, {author}'
release = metadata.version("siriuspy")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.viewcode',
	'sphinx.ext.napoleon'
]

autodoc_default_options = {
	"members": True,
	"undoc-members": True,
	"private-members": True
}

source_suffix = ['.rst', '.md']
templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_context = {
    "display_github": True,
    "github_user": "lnls-sirius",
    "github_repo": "hla",
    "github_version": "master",
    "conf_py_path": "/siriuspy/docs/source/"
}

