"""Sphinx configuration for the context-db docs site."""

project = "context-db"
author = "context-db contributors"
copyright = "2026, context-db contributors"

extensions = ["myst_parser"]
source_suffix = {".md": "markdown"}
root_doc = "index"
exclude_patterns = ["_build", "requirements.txt"]

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

html_theme = "pydata_sphinx_theme"
html_title = "context-db"
html_logo = "_static/context-db-icon.svg"
html_favicon = "_static/favicon.svg"
html_static_path = ["_static"]
html_show_sourcelink = False

html_theme_options = {
    "logo": {"text": "context-db"},
    "github_url": "https://github.com/cart0113/context-db",
    "navbar_align": "left",
    "show_toc_level": 2,
    "navigation_with_keys": False,
    "secondary_sidebar_items": ["page-toc"],
    "footer_start": ["copyright"],
    "footer_end": [],
}
html_sidebars = {"index": []}
