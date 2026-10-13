"""Public English/Arabic documentation; build output is bundled in the wheel."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
from lecture_studio import __version__
project = 'Jupyter Lecture Studio'
author = 'aoos101'
copyright = '2026, Jupyter Lecture Studio contributors'
release = __version__
extensions = ['myst_parser', 'sphinx.ext.autodoc', 'sphinx.ext.napoleon']
source_suffix = {'.md': 'markdown', '.rst': 'restructuredtext'}
exclude_patterns = ['_build', 'images', 'DESIGN_PARITY.md', 'VERIFICATION.md', 'DEVELOPMENT.md', 'PUBLISHING.md', 'PDF_VERIFICATION.md']
html_theme = 'furo'
html_title = 'Jupyter Lecture Studio — Animated Jupyter Lectures'
html_static_path = ['_static']
html_css_files = ['studio-docs.css']
html_theme_options = {
    'light_css_variables': {'color-brand-primary': '#705427', 'color-brand-content': '#705427'},
    'dark_css_variables': {'color-brand-primary': '#ecd29a', 'color-brand-content': '#ecd29a'},
}
myst_enable_extensions = ['colon_fence']
autodoc_typehints = 'description'
autodoc_member_order = 'bysource'
html_copy_source = False
html_show_sourcelink = False

templates_path = ['_templates']
# MyST's autodoc bridge currently requires the pre-Sphinx-9 documenter API.
autodoc_use_legacy_class_based = True
