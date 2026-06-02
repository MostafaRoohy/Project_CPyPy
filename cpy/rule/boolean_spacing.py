"""
boolean_spacing — enforce double spaces around ``and`` / ``or`` inside conditions.

The rule only runs on condition-bearing lines (``if`` / ``elif`` / ``while`` / ``assert``) to match
the documented intent and avoid surprising edits elsewhere.  Matching is done on the *masked* line
so ``and`` / ``or`` appearing inside strings or comments are never touched, and word boundaries stop
us from hitting substrings like ``brand`` or ``order``.
"""

from __future__ import annotations

import re

from cpy.model.line import CONDITION_KEYWORDS, Line
from cpy.rule.base import Context
from cpy.util.text import mask_strings

#######################################################################################################
# BooleanSpacing
#

_OP = re.compile(r"\s+(and|or)\s+")

class BooleanSpacing:

    name = "boolean_spacing"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx: Context) -> list[Line]:

        for line in lines:

            if (line.is_continuation):

                continue
            #
            if (line.keyword() not in CONDITION_KEYWORDS):

                continue
            #

            (code, comment) = line.split_comment()
            shift           = len(line.indent)
            local           = [(s - shift, e - shift) for (s, e) in line.string_spans]
            masked          = mask_strings(code, local)

            matches = list(_OP.finditer(masked))
            if (not matches):

                continue
            #

            # Apply replacements right-to-left on the real code so indices stay valid.
            new_code = code
            for m in reversed(matches):

                op       = m.group(1)
                new_code = new_code[:m.start()] + "  " + op + "  " + new_code[m.end():]
            #

            rebuilt = new_code + (("  " + comment) if comment else "")
            if (rebuilt != line.content):

                line.set_content(rebuilt)
            #
        #

        return (lines)
    #
#
