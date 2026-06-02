"""
block_end_marker — insert standalone ``#`` lines that explicitly close indented blocks.

Strategy (guarantees idempotence): first remove every existing *structural* marker — a line whose
content is exactly ``#`` — then recompute markers from scratch with an indent stack.  Because banner
lines (``####…``) and real comments (``# note``) never equal exactly ``#``, they survive untouched.

The ``if/elif/else`` and ``try/except/finally`` chains are treated as a single block: intermediate
clauses do not get a marker; only the final close of the whole chain (or end of file) does.
"""

from __future__ import annotations

from collections import defaultdict

from cpy.model.block import BlockFrame
from cpy.model.line import BLOCK_KEYWORDS, Line
from cpy.util.text import find_last_top_level, mask_strings

#######################################################################################################
# BlockEndMarker
#

_CONTINUATION_KW = frozenset({"elif", "else", "except", "finally"})

class BlockEndMarker:

    name = "block_end_marker"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx) -> list[Line]:

        kept = [ln for ln in lines if ln.content != "#"]

        stack        : list[BlockFrame]   = []
        insertions   : list[tuple[int, int]] = []   # (insert_after_index, indent_width)
        last_nonblank: int                = -1

        for (i, ln) in enumerate(kept):

            if (ln.is_blank):

                continue
            #
            if (ln.is_comment  or  ln.is_continuation):

                last_nonblank = i
                continue
            #

            width = ln.indent_width()
            kw    = ln.keyword()

            # Close every block we have dedented out of.
            while (len(stack) > 0  and  width <= stack[-1].indent):

                if (width == stack[-1].indent  and  kw in _CONTINUATION_KW):

                    break
                #
                frame = stack.pop()
                insertions.append((last_nonblank, frame.indent))
            #

            if (self._is_header(ln, kw)):

                if (kw in _CONTINUATION_KW  and  len(stack) > 0  and  stack[-1].indent == width):

                    stack[-1].keyword = kw
                else:

                    stack.append(BlockFrame(keyword=kw, indent=width))
                #
            #

            last_nonblank = i
        #

        while (len(stack) > 0):

            frame = stack.pop()
            insertions.append((last_nonblank, frame.indent))
        #

        if (len(insertions) == 0):

            return (kept)
        #

        by_pos: dict[int, list[int]] = defaultdict(list)
        for (pos, indent) in insertions:

            by_pos[pos].append(indent)
        #

        result: list[Line] = []
        for (i, ln) in enumerate(kept):

            result.append(ln)
            for indent in by_pos.get(i, []):

                result.append(self._marker(indent))
            #
        #

        return (result)
    #

    #---------------------------------------------------------------------------------------------#

    def _is_header(self, line: Line, kw: str | None) -> bool:

        if (kw not in BLOCK_KEYWORDS):

            return (False)
        #

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

    def _marker(self, indent: int) -> Line:

        pad = " " * indent

        return (Line(
            raw             = pad + "#",
            indent          = pad,
            content         = "#",
            is_blank        = False,
            is_comment      = True,
            is_continuation = False,
            string_spans    = [],
        ))
    #
#
