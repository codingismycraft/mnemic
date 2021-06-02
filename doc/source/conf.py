#!/usr/bin/env python3

import alabaster
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                           '..', 'dolon', '_version.py')

sys.path.append(os.path.abspath('../..'))
sys.path.append(os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('..'))


with open(version_file, 'r') as f:
    for line in f:
        if line.startswith('__version__ ='):
            _, _, version = line.partition('=')
            version = version.strip(" \n'\"")
            break
    else:
        raise RuntimeError(
            'unable to read the version from dolon/_version.py')

# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.intersphinx',
]

add_module_names = False

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'dolon'
copyright = 'John Pazarzis'
author = 'John Pazarzis'
release = version
language = None
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_todos = False
suppress_warnings = ['image.nonlocal_uri']

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'
# html_theme_options = {
#     'description': 'asyncpg is a fast PostgreSQL client library for the '
#                    'Python asyncio framework',
#     'show_powered_by': False,
# }
html_theme_path = [alabaster.get_path()]
html_title = 'dolon Documentation'
html_short_title = 'dolon'
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
    ]
}
html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = True
html_context = {
    'css_files': [
        '_static/theme_overrides.css',
    ],
}
htmlhelp_basename = 'dolondoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

latex_documents = [
    (master_doc, 'dolon.tex', 'dolon Documentation',
     author, 'manual'),
]


# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
    (master_doc, 'dolon', 'dolon Documentation',
     author, 'dolon',
     'dolon is a tracing library talking to mnemic'),
]

# -- Options for intersphinx ----------------------------------------------

intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}