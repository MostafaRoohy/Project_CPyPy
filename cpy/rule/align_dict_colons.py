"""
align_dict_colons — align colons in simple, one-entry-per-line dict literals (optional, off by
default).

Conservative by design: a line qualifies as a dict entry only when it is a *continuation* line
(i.e. inside an open bracket), opens no bracket of its own, and has exactly one top-level ``:`` with
a string- or identifier-looking key.  Consecutive qualifying lines at the same indent form a group
whose colons are aligned.  Anything else breaks the group, so slices / annotations / nested dicts
are left alone.
"""

from __future__ import annotations

import re

from cpy.model.line import Line
from cpy.rule.base import Context
from cpy.util.text import bracket_depth_scan, is_balanced, mask_strings

#######################################################################################################
# AlignDictColons
#

_KEY = re.compile(r"""^(?:"[^"]*"|'[^']*'|[A-Za-z_]\w*|\d+)$""")

class AlignDictColons:

    name = "align_dict_colons"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx: Context) -> list[Line]:

        group : list[tuple[Line, str, str, str]] = []   # (line, key, value, comment)
        indent: str | None                        = None

        def flush() -> None:

            if (len(group) == 0):

                return
            #

            width = max(len(key) for (_, key, _, _) in group)
            for (line, key, value, comment) in group:

                new_code = key.ljust(width) + " : " + value
                rebuilt  = new_code + (("  " + comment) if comment else "")
                if (rebuilt != line.content):

                    line.set_content(rebuilt)
                #
            #
            group.clear()
        #

        for line in lines:

            parsed = self._parse(line)
            if (parsed is None  or  (indent is not None  and  line.indent != indent)):

                flush()
                indent = None
            #
            if (parsed is not None):

                (key, value, comment) = parsed
                indent                = line.indent
                group.append((line, key, value, comment))
            #
        #

        flush()

        return (lines)
    #

    #---------------------------------------------------------------------------------------------#

    def _parse(self, line: Line) -> tuple[str, str, str] | None:

        if (not line.is_continuation  or  line.is_blank  or  line.is_comment):

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
        colons = [i for (i, ch) in enumerate(masked) if (ch == ":"  and  depths[i] == 0)]
        if (len(colons) != 1):

            return (None)
        #

        colon = colons[0]
        key   = code[:colon].strip()
        rest  = code[colon + 1:].strip()

        if (not _KEY.match(key)):

            return (None)
        #
        if (rest == ""):

            return (None)
        #

        return (key, rest, comment)
    #
#
