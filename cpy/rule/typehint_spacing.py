"""
typehint_spacing — normalise spacing in single-line ``def`` headers (optional, off by default).

Conventions enforced (see ``doc/cpy_rules.md`` section D):

* parameter annotations have no space around the ``:``      -> ``x:int``
* default values have no spaces around ``=``                -> ``ddof:int=1``
* the return arrow is spaced                                -> ``) -> Type:``

Only single-physical-line ``def`` / ``async def`` headers are handled; multi-line signatures are
left untouched.  All delimiter detection runs on the masked line so commas / colons inside string
defaults are never mistaken for syntax.
"""

from __future__ import annotations

from cpy.model.line import Line
from cpy.rule.base import Context
from cpy.util.text import bracket_depth_scan, is_balanced, mask_strings

#######################################################################################################
# TypehintSpacing
#

_NOT_PLAIN_BEFORE = set("=!<>+-*/%&|^@:~")

class TypehintSpacing:

    name = "typehint_spacing"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx: Context) -> list[Line]:

        for line in lines:

            if (line.is_continuation):

                continue
            #
            if (line.keyword() not in ("def", "async")):

                continue
            #

            (code, comment) = line.split_comment()
            shift           = len(line.indent)
            local           = [(s - shift, e - shift) for (s, e) in line.string_spans]
            masked          = mask_strings(code, local)

            if (not code.rstrip().endswith(":")  or  not is_balanced(masked)):

                continue
            #

            open_i = masked.find("(")
            if (open_i == -1):

                continue
            #

            depths  = bracket_depth_scan(masked)
            close_i = -1
            for j in range(open_i, len(masked)):

                if (masked[j] == ")"  and  depths[j] == 1):

                    close_i = j
                    break
                #
            #
            if (close_i == -1):

                continue
            #

            prefix   = code[:open_i].rstrip()
            params   = self._params(code, masked, depths, open_i + 1, close_i)
            new_after = self._after(code[close_i + 1:])

            new_code = prefix + "(" + ", ".join(params) + ")" + new_after
            rebuilt  = new_code + (("  " + comment) if comment else "")
            if (rebuilt != line.content):

                line.set_content(rebuilt)
            #
        #

        return (lines)
    #

    #---------------------------------------------------------------------------------------------#

    def _params(self, code: str, masked: str, depths: list[int], lo: int, hi: int) -> list[str]:

        # Split on depth-1 commas.
        bounds = [lo]
        for j in range(lo, hi):

            if (masked[j] == ","  and  depths[j] == 1):

                bounds.append(j)        # comma position acts as separator
            #
        #
        bounds.append(hi)

        params: list[str] = []
        start = lo
        for sep in bounds[1:]:

            seg_lo = start
            seg_hi = sep
            if (code[seg_lo:seg_hi].strip() != ""):

                params.append(self._norm_param(code, masked, depths, seg_lo, seg_hi))
            #
            start = sep + 1
        #

        return (params)
    #

    def _norm_param(self, code: str, masked: str, depths: list[int], lo: int, hi: int) -> str:

        colon = -1
        eq    = -1
        for j in range(lo, hi):

            if (depths[j] != 1):

                continue
            #
            if (masked[j] == ":"  and  colon == -1):

                colon = j
            #
            if (masked[j] == "="  and  eq == -1):

                nxt  = masked[j + 1] if (j + 1 < hi) else ""
                prev = masked[j - 1] if (j - 1 >= lo) else ""
                if (nxt != "="  and  prev not in _NOT_PLAIN_BEFORE):

                    eq = j
                #
            #
        #

        name_end = min(x for x in (colon, eq, hi) if x != -1)
        name     = code[lo:name_end].strip()

        result = name
        if (colon != -1):

            type_end = eq if (eq != -1) else hi
            result  += ":" + code[colon + 1:type_end].strip()
        #
        if (eq != -1):

            result += "=" + code[eq + 1:hi].strip()
        #

        return (result)
    #

    def _after(self, after: str) -> str:

        arrow = after.find("->")
        if (arrow == -1):

            return (":")
        #

        colon = after.rstrip().rfind(":")
        ret   = after[arrow + 2:colon].strip()

        return (" -> " + ret + ":")
    #
#
