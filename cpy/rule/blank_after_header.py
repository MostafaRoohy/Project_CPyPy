"""
blank_after_header — ensure one blank line after every ``class`` / ``def`` header.

The personal style always separates a class/def header from its first body line (and even from a
leading docstring) with a single blank line.  Multi-line signatures are handled by walking over the
continuation lines to the real header end; one-liners (``class X: pass``) are left untouched.

Two-pass like ``block_end_marker``: collect insertion points, then rebuild the list inserting one
blank ``Line`` after each header.  Idempotent — if a blank already follows the header, nothing is
inserted.
"""

from __future__ import annotations

from cpy.model.line import Line
from cpy.util.text import find_last_top_level, mask_strings

#######################################################################################################
# BlankAfterHeader
#

class BlankAfterHeader:

    name = "blank_after_header"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx) -> list[Line]:

        insert_after: set[int] = set()
        n = len(lines)
        i = 0

        while (i < n):

            if (not self._is_header_start(lines[i])):

                i += 1
                continue
            #

            # Walk over continuation lines to the physical end of the header.
            j = i
            while (j + 1 < n  and  lines[j + 1].is_continuation):

                j += 1
            #

            if (self._ends_header(lines[j])  and  j + 1 < n  and  not lines[j + 1].is_blank):

                insert_after.add(j)
            #

            i = j + 1
        #

        if (len(insert_after) == 0):

            return (lines)
        #

        result: list[Line] = []
        for (idx, line) in enumerate(lines):

            result.append(line)
            if (idx in insert_after):

                result.append(self._blank())
            #
        #

        return (result)
    #

    #---------------------------------------------------------------------------------------------#

    def _is_header_start(self, line: Line) -> bool:

        if (line.is_blank  or  line.is_comment  or  line.is_continuation):

            return (False)
        #

        kw = line.keyword()
        if (kw in ("class", "def")):

            return (True)
        #
        if (kw == "async"):

            parts = line.content.split(maxsplit=2)

            return (len(parts) >= 2  and  parts[1] == "def")
        #

        return (False)
    #

    def _ends_header(self, line: Line) -> bool:
        """True when this line's code ends with the block ``:`` (i.e. it is a real header end)."""

        (code, _comment) = line.split_comment()
        rstripped        = code.rstrip()
        if (not rstripped.endswith(":")):

            return (False)
        #

        shift  = len(line.indent)
        local  = [(s - shift, e - shift) for (s, e) in line.string_spans]
        masked = mask_strings(code, local)

        return (find_last_top_level(masked, ":") == len(rstripped) - 1)
    #

    def _blank(self) -> Line:

        return (Line(
            raw             = "",
            indent          = "",
            content         = "",
            is_blank        = True,
            is_comment      = False,
            is_continuation = False,
            string_spans    = [],
        ))
    #
#
