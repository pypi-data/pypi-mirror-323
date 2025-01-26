# from pathlib import Path
# def SPHINX_CONF(project_name, author, description=None, css_file=None, js_file=None, myst_parser=False, theme="furo"):
#     # Create extensions list
#     extensions = [
#         "sphinx.ext.autodoc",
#         "sphinx.ext.viewcode",
#         "sphinx.ext.napoleon", 
#         "sphinx.ext.githubpages",
#         "sphinx.ext.autosummary",
#         "sphinx_design"
#     ]
    
#     if myst_parser:
#         extensions.append("myst_parser")
    
#     return f"""
# # Configuration file for Sphinx
# import os
# import sys
# sys.path.insert(0, {Path(project_name).resolve()})

# project = "{project_name}"
# author = "{author}"
# copyright = "2024, {author}"

# # Add extensions
# extensions = {extensions}

# # Enable autosummary and set its options
# autosummary_generate = True
# autosummary_imported_members = True
# add_module_names = False

# # Source settings
# source_suffix = {{
#     '.rst': 'restructuredtext'{',' if myst_parser else ''}
#     {".md': 'markdown'" if myst_parser else ""}
# }}

# # HTML output settings
# html_theme = {'\"' + theme + '\"' if theme else '"furo"'}
# html_static_path = ['_static']
# templates_path = ['_templates']
# exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']

# # Theme options
# html_theme_options = {{
#     "sidebar_hide_name": False,
#     "navigation_with_keys": True,
#     "announcement": "⚡ Currently in beta!",
# }}

# # Napoleon settings
# napoleon_google_docstring = True
# napoleon_numpy_docstring = True
# napoleon_include_init_with_doc = True
# napoleon_include_private_with_doc = True
# napoleon_include_special_with_doc = True
# napoleon_use_admonition_for_examples = True
# napoleon_use_admonition_for_notes = True
# napoleon_use_rtype = True
# napoleon_preprocess_types = True

# # Autodoc settings
# autodoc_default_options = {{
#     'members': True,
#     'member-order': 'bysource',
#     'undoc-members': True,
#     'show-inheritance': True,
# }}

# # Master doc
# master_doc = 'index'
# """ + (f"""
# html_css_files = [
#     "{css_file}",
# ]
# """ if css_file else "") + (f"""
# # Optionally, add custom JavaScript files
# html_js_files = [
#     "{js_file}",
# ]
# """ if js_file else "")

# SPHINX_INDEX = """
# {project_name}
# {'=' * (len(project_name) + 2)}

# {description}

# .. toctree::
#    :maxdepth: 2
#    :caption: Contents:
#    :hidden:

#    getting_started
#    api/index

# .. panels::
#    :container: container-lg pb-3
#    :column: col-lg-6 col-md-6 col-sm-12 col-xs-12 p-2

#    Getting Started
#    ^^^^^^^^^^^^^^
#    Quick start guide and installation instructions.
   
#    +++
#    :link: getting_started
   
#    ---
   
#    API Reference
#    ^^^^^^^^^^^^
#    Detailed API documentation.
   
#    +++
#    :link: api/index

# """

# SPHINX_API = """
# {project_name} API Reference
# ============================

# .. toctree::
#    :maxdepth: 2
#    :caption: Modules:

#    {module_name}

# .. automodule:: {module_name}
#    :members:
#    :undoc-members:
#    :show-inheritance:
# """ 


# SPHINX_MAKEFILE = """# Minimal makefile for Sphinx documentation
# SPHINXOPTS    ?=
# SPHINXBUILD   ?= sphinx-build
# SOURCEDIR     = .
# BUILDDIR      = _build

# help:
# 	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# .PHONY: help Makefile clean html

# %: Makefile
# 	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# clean:
# 	rm -rf $(BUILDDIR)/*

# html:
# 	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
# """
