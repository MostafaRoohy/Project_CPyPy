"""
align_assignments — align ``=`` within contiguous groups of plain assignments.

A *group* is a maximal run of consecutive lines that share the same indentation and are each a plain
``name = value`` assignment.  A blank line, a comment line, or any non-assignment code line breaks
the group (this is what keeps the README's visually separated blocks separate).

Only a genuine assignment ``=`` counts: comparisons (``==`` ``<=`` ``>=`` ``!=``), the walrus
``:=``, augmented assignments (``+=`` …) and keyword arguments inside calls (``=`` at bracket depth
> 0) are all rejected.  Every line is rebuilt from its stripped left-hand side, so re-running is a
no-op.
"""

from __future__ import annotations

from cpy.model.line import Line
from cpy.rule.base import Context
from cpy.util.text import bracket_depth_scan, is_balanced, mask_strings

#######################################################################################################
# Helpers
#

# Characters that, immediately before an '=', mean it is NOT a plain assignment.
_NOT_PLAIN_BEFORE = set("=!<>+-*/%&|^@:~")

def _find_assign_eq(masked: str) -> int:
    """Index of the plain assignment ``=`` at bracket depth 0, or ``-1`` if the line has none."""

    depths = bracket_depth_scan(masked)
    for (i, ch) in enumerate(masked):

        if (ch != "="  or  depths[i] != 0):

            continue
        #
        if (i + 1 < len(masked)  and  masked[i + 1] == "="):

            continue        # '=='
        #
        if (i > 0  and  masked[i - 1] in _NOT_PLAIN_BEFORE):

            continue        # '==', '<=', '+=', ':=', ...
        #

        return (i)
    #

    return (-1)
#

#######################################################################################################
# AlignAssignments
#

class AlignAssignments:

    name = "align_assignments"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx: Context) -> list[Line]:

        group: list[tuple[Line, str, str, str]] = []   # (line, indent, lhs, rhs[+comment])

        def flush() -> None:

            if (len(group) == 0):

                return
            #

            field = max(len(lhs) for (_, _, lhs, _) in group)
            for (line, indent, lhs, tail) in group:

                line.set_content(lhs.ljust(field) + " = " + tail)
            #
            group.clear()
        #

        current_indent: str | None = None

        for line in lines:

            parsed = self._parse(line)

            if (parsed is None  or  (current_indent is not None  and  line.indent != current_indent)):

                flush()
                current_indent = None
            #

            if (parsed is not None):

                (lhs, tail) = parsed
                if (current_indent is None):

                    current_indent = line.indent
                #
                group.append((line, line.indent, lhs, tail))
            #
        #

        flush()

        return (lines)
    #

    #---------------------------------------------------------------------------------------------#

    def _parse(self, line: Line) -> tuple[str, str] | None:
        """Return ``(lhs, rhs_plus_comment)`` for an alignable line, else ``None``."""

        if (line.is_blank  or  line.is_comment  or  line.is_continuation):

            return (None)
        #

        (code, comment) = line.split_comment()
        shift           = len(line.indent)
        local           = [(s - shift, e - shift) for (s, e) in line.string_spans]
        masked          = mask_strings(code, local)

        if (not is_balanced(masked)):

            return (None)        # RHS opens a bracket continued on the next line.
        #

        eq = _find_assign_eq(masked)
        if (eq == -1):

            return (None)
        #

        lhs = code[:eq].rstrip()
        rhs = code[eq + 1:].strip()
        if (lhs == ""):

            return (None)
        #

        tail = rhs + (("  " + comment) if comment else "")

        return (lhs, tail)
    #
#
