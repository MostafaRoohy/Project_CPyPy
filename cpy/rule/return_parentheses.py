"""
return_parentheses — enforce ``return (value)``.

Bare ``return`` (no value) is never touched.  An already fully parenthesised value is left as-is so
the rule is idempotent.  Multi-line returns (value opens a bracket that closes on a later line) are
skipped in this version.
"""

from __future__ import annotations

from cpy.model.line import Line
from cpy.rule.base import Context
from cpy.util.text import is_balanced, is_fully_wrapped, mask_strings

#######################################################################################################
# ReturnParentheses
#

class ReturnParentheses:

    name = "return_parentheses"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx: Context) -> list[Line]:

        for line in lines:

            if (line.is_continuation):

                continue
            #
            if (line.keyword() != "return"):

                continue
            #

            (code, comment) = line.split_comment()
            masked          = mask_strings(code, _local_spans(line))

            # Drop the 'return' keyword and inspect the value.
            value        = code[len("return"):]
            value_masked = masked[len("return"):]

            stripped        = value.strip()
            stripped_masked = value_masked.strip()

            if (stripped == ""):

                # bare return — leave untouched.
                continue
            #
            if (not is_balanced(stripped_masked)):

                # multi-line return; skip in v1.
                continue
            #
            if (is_fully_wrapped(stripped_masked)):

                new_code = "return " + stripped
            else:

                new_code = "return (" + stripped + ")"
            #

            rebuilt = new_code + (("  " + comment) if comment else "")
            if (rebuilt != line.content):

                line.set_content(rebuilt)
            #
        #

        return (lines)
    #
#

def _local_spans(line: Line) -> list[tuple[int, int]]:

    shift = len(line.indent)

    return ([(s - shift, e - shift) for (s, e) in line.string_spans])
#
