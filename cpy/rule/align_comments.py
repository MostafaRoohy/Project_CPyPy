"""
align_comments — align trailing ``#`` comments to a common column within a stacked group.

For a run of consecutive same-indent code lines that each carry a trailing comment, the comments are
pushed out to a shared column (two spaces past the widest code part):

    ser_open      : pd.Series  # float64
    ser_high      : pd.Series  # float64

Unlike the alignment rules, comment groups **break on blank lines** (matching the user's style where
the ``pd.Series`` block and the following ``np.ndarray`` block have comments at different columns).
A comment-only line, an indent change, or a line without a trailing comment also breaks the group.
Runs after the content/alignment rules so it sees final code widths.
"""

from __future__ import annotations

from cpy.model.line import Line
from cpy.rule.base import Context

#######################################################################################################
# AlignComments
#

class AlignComments:

    name = "align_comments"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx: Context) -> list[Line]:

        group : list[tuple[Line, str, str]] = []   # (line, code, comment)
        indent: str | None                   = None

        def flush() -> None:

            if (len(group) == 0):

                return
            #

            col = max(len(code) for (_, code, _) in group)
            for (line, code, comment) in group:

                line.set_content(code.ljust(col) + "  " + comment)
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

    def _parse(self, line: Line) -> tuple[str, str] | None:
        """Return ``(code, comment)`` for a code line that has a trailing comment, else ``None``."""

        if (line.is_blank  or  line.is_comment  or  line.is_continuation):

            return (None)
        #

        (code, comment) = line.split_comment()

        if (comment == ""  or  code.strip() == ""):

            return (None)
        #

        return (code.rstrip(), comment)
    #
#
