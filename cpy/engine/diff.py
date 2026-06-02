"""
Unified diff helper for ``cpy diff`` and CI-style workflows.
"""

from __future__ import annotations

import difflib

#######################################################################################################
# make_diff
#

def make_diff(original: str, formatted: str, path: str = "<stdin>") -> str:

    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile = f"{path} (original)",
        tofile   = f"{path} (formatted)",
    )

    return ("".join(diff))
#
