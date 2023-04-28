# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Corpus Annotation Graph (CAG)'
copyright = '2023, Roxanne El Baff. Tobias Hecking'
author = 'Roxanne El Baff, Tobias Hecking'
release = '1.5.0'
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

pygments_style = 'sphinx'

# generate autosummary even if no references
autosummary_generate = True
autoclass_content = "both"

todo_include_todos = False
templates_path = ["_templates"]
exclude_patterns = []
numfig = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_style = ['css/custom.css']

html_theme_options = {
    'description': 'An architectural framework for graph management',
    'github_user': 'DLR-SC',
    'github_repo': 'corpus-annotation-graph-builder',
    'github_type': 'star',
    'github_button': True,
    'github_banner': True,
    'github_count ': True
    }
#pygments_style = "xcode"