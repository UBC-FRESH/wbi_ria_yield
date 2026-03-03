from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path


project = "wbi_ria_yield"
master_doc = "index"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
if find_spec("nbsphinx"):
    extensions.append("nbsphinx")

autosummary_generate = True
exclude_patterns = ["_build", "**.ipynb_checkpoints"]

if find_spec("sphinx_rtd_theme"):
    html_theme = "sphinx_rtd_theme"
else:
    html_theme = "alabaster"

_static_dir = Path(__file__).with_name("_static")
html_static_path = ["_static"] if _static_dir.exists() else []
