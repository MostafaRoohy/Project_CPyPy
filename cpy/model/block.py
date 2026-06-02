"""
Minimal indentation model.

Only :mod:`cpy.rule.block_end_marker` needs real block awareness, so this module stays deliberately
tiny: a single frame describing an open block.  No tree, no statement parsing.
"""

from __future__ import annotations

from dataclasses import dataclass

#######################################################################################################
# BlockFrame
#

@dataclass
class BlockFrame:

    keyword    : str
    indent     : int
    body_indent: int | None = None
#
