"""
dj-payfast: Django PayFast Integration Library
A comprehensive Django library for PayFast payment gateway integration in South Africa

PROJECT STRUCTURE:
==================

dj-payfast/
├── README.md
├── LICENSE
├── setup.py
├── requirements.txt
├── MANIFEST.in
├── .gitignore
│
├── payfast/                          # Main package directory
│   ├── __init__.py                   # Package initialization, version info
│   ├── apps.py                       # Django app configuration
│   ├── conf.py                       # Settings and configuration
│   ├── models.py                     # Database models (Payment, Notification)
│   ├── forms.py                      # PayFast payment form
│   ├── views.py                      # Webhook handler views
│   ├── utils.py                      # Signature generation, validation
│   ├── admin.py                      # Django admin configuration
│   ├── urls.py                       # URL routing for webhooks
│   ├── signals.py                    # Django signals (optional)
│   ├── exceptions.py                 # Custom exceptions (optional)
│   │
│   ├── migrations/                   # Database migrations
│   │   └── __init__.py
│   │
│   ├── management/                   # Management commands
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── payfast_test.py       # Test payment command
│   │
│   └── templates/                    # Optional template examples
│       └── payfast/
│           └── payment_form.html     # Example payment template
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── test_models.py                # Model tests
│   ├── test_views.py                 # View/webhook tests
│   ├── test_forms.py                 # Form tests
│   ├── test_utils.py                 # Utility function tests
│   └── test_signals.py               # Signal tests
│
├── docs/                             # Documentation
│   ├── conf.py                       # Sphinx configuration
│   ├── index.rst
│   ├── installation.rst
│   ├── quickstart.rst
│   ├── configuration.rst
│   ├── usage.rst
│   └── api.rst
│
└── example_project/                  # Example Django project
    ├── manage.py
    ├── example_project/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    │
    └── shop/                         # Example app using dj-payfast
        ├── __init__.py
        ├── views.py
        ├── urls.py
        └── templates/
            └── shop/
                ├── checkout.html
                ├── success.html
                └── cancel.html

INSTALLATION:
=============
pip install dj-payfast

SETTINGS.PY CONFIGURATION:
==========================
INSTALLED_APPS = [
    ...
    'payfast',
]

PAYFAST_MERCHANT_ID = 'your_merchant_id'
PAYFAST_MERCHANT_KEY = 'your_merchant_key'
PAYFAST_PASSPHRASE = 'your_passphrase'
PAYFAST_TEST_MODE = True

URLS.PY CONFIGURATION:
======================
urlpatterns = [
    ...
    path('payfast/', include('payfast.urls')),
]
"""

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
import django

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../payfast'))

# Setup Django settings for autodoc
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()


# -- Project information -----------------------------------------------------

project = 'dj-payfast'
copyright = '2024, Your Name'
author = 'Your Name'

# The full version, including alpha/beta/rc tags
release = '0.1.0'
version = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
    'sphinx_copybutton',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = ['.rst', '.md']

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = 'en'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    '**': [
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = '_static/logo.png'

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = '_static/favicon.ico'

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

# Output file base name for HTML help builder.
htmlhelp_basename = 'dj-payfastdoc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',

    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    'preamble': '',

    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'dj-payfast.tex', 'dj-payfast Documentation',
     'Your Name', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'dj-payfast', 'dj-payfast Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'dj-payfast', 'dj-payfast Documentation',
     author, 'dj-payfast', 'Django PayFast integration library.',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'django': ('https://docs.djangoproject.com/en/stable/', 
               'https://docs.djangoproject.com/en/stable/_objects/'),
}

# -- Options for autodoc extension -------------------------------------------

# This value selects what content will be inserted into the main body of an
# autoclass directive.
autoclass_content = 'both'

# This value selects if automatically documented members are sorted alphabetical
# (value 'alphabetical'), by member type (value 'groupwise') or by source order
# (value 'bysource').
autodoc_member_order = 'bysource'

# This value is a list of autodoc directive flags that should be automatically
# applied to all autodoc directives.
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# -- Options for napoleon extension ------------------------------------------

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for copybutton extension ----------------------------------------

# Exclude prompts and output from copy
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- Custom configuration ----------------------------------------------------

# Add custom CSS
def setup(app):
    """Add custom configuration"""
    app.add_css_file('custom.css')

# Autosummary settings
autosummary_generate = True

# Linkcheck settings
linkcheck_ignore = [
    r'http://localhost:\d+/',
]

# Nitpicky mode - warn about all references where the target cannot be found
nitpicky = False
nitpick_ignore = [
    ('py:class', 'django.db.models.Model'),
]