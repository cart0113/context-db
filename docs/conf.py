"""Sphinx configuration for the context-db docs site.

Pages are Markdown (MyST). The look is the PyData theme plus _static/custom.css.
Build with:  sphinx-build -W docs docs/_build/html
"""

project = "context-db"
author = "context-db contributors"
copyright = "2026, context-db contributors"

extensions = ["myst_parser", "sphinx_design", "sphinx_copybutton"]
source_suffix = {".md": "markdown"}
root_doc = "index"
exclude_patterns = ["_build", "requirements.txt"]

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

SITE = "https://cart0113.github.io/context-db/"
TAGLINE = (
    "Agent skills that keep a Markdown knowledge base in your repo. "
    "Built on the Open Knowledge Format (OKF)."
)
myst_html_meta = {
    "description lang=en": TAGLINE,
    "property=og:title": "context-db",
    "property=og:description": TAGLINE,
    "property=og:image": SITE + "_static/og-image.png",
    "property=og:type": "website",
}

html_theme = "pydata_sphinx_theme"
html_title = "context-db"
html_baseurl = SITE
html_logo = "_static/context-db-icon.svg"
html_favicon = "_static/favicon.svg"
html_static_path = ["_static"]
templates_path = ["_templates"]
# JetBrains Mono is the heading font; custom.css names it.
html_css_files = [
    "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700;800&display=swap",
    "custom.css",
    "looks.css",
]
# The look picker, for trying out style ideas. Delete with looks.css once they are chosen.
html_js_files = ["looks.js"]
# Pages open in light mode. The switch in the header still offers dark.
html_context = {"default_mode": "light"}
html_show_sourcelink = False

html_theme_options = {
    "logo": {"text": "context-db"},
    "github_url": "https://github.com/cart0113/context-db",
    "header_links_before_dropdown": 4,
    "navbar_align": "left",
    "show_toc_level": 2,
    "navigation_with_keys": False,
    "secondary_sidebar_items": ["page-toc"],
    "pygments_light_style": "github-light",
    "pygments_dark_style": "github-dark",
    "footer_start": ["copyright"],
    "footer_end": [],
}

# Every page is top level, so the left sidebar would always be empty.
html_sidebars = {"**": []}
