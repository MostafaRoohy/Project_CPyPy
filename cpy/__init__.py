"""
CPy — a Python formatter targeting a specific non-PEP8 personal style.

Public API:

    from cpy import format_text
    format_text(source_code) -> formatted_code
"""

from __future__ import annotations

from cpy.config import Config, load_config
from cpy.engine.formatter import format_file, format_paths, format_text

__version__ = "0.1.0"

__all__ = [
    "format_text",
    "format_file",
    "format_paths",
    "Config",
    "load_config",
    "__version__",
]
