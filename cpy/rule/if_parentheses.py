"""
if_parentheses — enforce ``if ( ... ):``, ``elif ( ... ):``, ``while ( ... ):``.

``for`` headers are intentionally left alone.  The block colon is found as the *last* depth-0 ``:``
so colons inside dicts, lambdas, slices or annotations in the condition do not confuse us.  Already
wrapped conditions and multi-line headers are skipped, keeping the rule idempotent and safe.
"""

from __future__ import annotations

from cpy.model.line import Line
from cpy.rule.base import Context
from cpy.util.text import find_last_top_level, is_fully_wrapped, mask_strings

#######################################################################################################
# IfParentheses
#

_KEYWORDS = ("if", "elif", "while")

class IfParentheses:

    name = "if_parentheses"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx: Context) -> list[Line]:

        for line in lines:

            if (line.is_continuation):

                continue
            #

            kw = line.keyword()
            if (kw not in _KEYWORDS):

                continue
            #

            (code, comment) = line.split_comment()
            shift           = len(line.indent)
            local           = [(s - shift, e - shift) for (s, e) in line.string_spans]
            masked          = mask_strings(code, local)

            colon = find_last_top_level(masked, ":")
            if (colon == -1  or  colon != len(code.rstrip()) - 1):

                # No real block colon at end (e.g. wrapped condition continues on next line) — skip.
                continue
            #

            cond        = code[len(kw):colon].strip()
            cond_masked = masked[len(kw):colon].strip()

            if (cond == ""):

                continue
            #
            if (is_fully_wrapped(cond_masked)):

                continue
            #

            new_code = kw + " (" + cond + "):"
            rebuilt  = new_code + (("  " + comment) if comment else "")
            if (rebuilt != line.content):

                line.set_content(rebuilt)
            #
        #

        return (lines)
    #
#
