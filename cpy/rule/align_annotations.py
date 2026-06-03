"""
align_annotations — align ``:`` (and ``=`` defaults) in groups of annotated declarations.

Targets statement-level annotated declarations such as dataclass fields, ``Protocol`` attributes and
``self.x : T = ...`` lines:

    name    : str
    kind    : Literal['int', 'float']
    low     : Optional[float]     = None
    high    : Optional[float]     = None

The ``:`` column is aligned across the group, and for the lines that carry a default the ``=`` column
is aligned too.  Grouping spans blank lines within the same indent block (a comment, indent change,
continuation, or non-annotation line breaks it).  This is distinct from ``typehint_spacing`` (function
parameters, no spaces) and ``align_assignments`` (plain ``x = y``, which it deliberately leaves alone).
"""

from __future__ import annotations

import re

from cpy.model.line import BLOCK_KEYWORDS, Line
from cpy.rule.base import Context
from cpy.util.text import bracket_depth_scan, is_balanced, mask_strings

#######################################################################################################
# Helpers
#

_TARGET           = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*$")
_NOT_PLAIN_BEFORE = set("=!<>+-*/%&|^@:~")

def _find_plain_eq(masked: str, depths: list[int], start: int) -> int:
    """First plain assignment ``=`` at depth 0 from ``start``, or ``-1``."""

    for i in range(start, len(masked)):

        if (masked[i] != "="  or  depths[i] != 0):

            continue
        #
        if (i + 1 < len(masked)  and  masked[i + 1] == "="):

            continue
        #
        if (i > 0  and  masked[i - 1] in _NOT_PLAIN_BEFORE):

            continue
        #

        return (i)
    #

    return (-1)
#

#######################################################################################################
# AlignAnnotations
#

class AlignAnnotations:

    name = "align_annotations"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx: Context) -> list[Line]:

        group : list[tuple[Line, str, str, str | None, str]] = []   # (line, target, type, default, comment)
        indent: str | None                                   = None

        def flush() -> None:

            if (len(group) == 0):

                return
            #

            name_w = max(len(target) for (_, target, _, _, _) in group)
            type_w = max((len(typ) for (_, _, typ, default, _) in group if default is not None), default=0)

            for (line, target, typ, default, comment) in group:

                new_code = target.ljust(name_w) + " : "
                if (default is not None):

                    new_code += typ.ljust(type_w) + " = " + default
                else:

                    new_code += typ
                #

                rebuilt = new_code + (("  " + comment) if comment else "")
                if (rebuilt != line.content):

                    line.set_content(rebuilt)
                #
            #
            group.clear()
        #

        for line in lines:

            if (line.is_blank):

                continue            # spans blank lines
            #

            parsed = self._parse(line)

            if (parsed is None  or  (indent is not None  and  line.indent != indent)):

                flush()
                indent = None
            #

            if (parsed is not None):

                if (indent is None):

                    indent = line.indent
                #
                group.append((line, *parsed))
            #
        #

        flush()

        return (lines)
    #

    #---------------------------------------------------------------------------------------------#

    def _parse(self, line: Line) -> tuple[str, str, str | None, str] | None:
        """Return ``(target, type, default|None, comment)`` for an annotation line, else ``None``."""

        if (line.is_blank  or  line.is_comment  or  line.is_continuation):

            return (None)
        #
        if (line.keyword() in BLOCK_KEYWORDS):

            return (None)
        #

        (code, comment) = line.split_comment()
        shift           = len(line.indent)
        local           = [(s - shift, e - shift) for (s, e) in line.string_spans]
        masked          = mask_strings(code, local)

        if (not is_balanced(masked)):

            return (None)
        #

        depths = bracket_depth_scan(masked)

        # First top-level ':'.
        colon = -1
        for (i, ch) in enumerate(masked):

            if (ch == ":"  and  depths[i] == 0):

                colon = i
                break
            #
        #
        if (colon == -1):

            return (None)
        #

        # Reject if a plain '=' appears before the ':' (then it's not a clean annotation).
        if (_find_plain_eq(masked, depths, 0) != -1  and  _find_plain_eq(masked, depths, 0) < colon):

            return (None)
        #

        target = code[:colon].strip()
        if (not _TARGET.match(target)):

            return (None)
        #

        eq = _find_plain_eq(masked, depths, colon + 1)
        if (eq == -1):

            typ     = code[colon + 1:].strip()
            default = None
        else:

            typ     = code[colon + 1:eq].strip()
            default = code[eq + 1:].strip()
        #

        if (typ == ""):

            return (None)
        #

        return (target, typ, default, comment)
    #
#
