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

class BlockEndMarker:

    name = "block_end_marker"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx) -> list[Line]:

        # Standalone '#' lines that sit next to a '###...' banner are section separators, not block
        # markers — preserve them. Every other exact-'#' line is a (re)computable block marker.
        protected = self._protected_markers(lines)
        kept      = [ln for (idx, ln) in enumerate(lines) if (ln.content != "#"  or  idx in protected)]

        stack     : list[BlockFrame]      = []
        insertions: list[tuple[int, int]] = []   # (insert_after_index, indent_width)

        for (i, ln) in enumerate(kept):

            if (ln.is_blank  or  ln.is_comment  or  ln.is_continuation):

                continue
            #

            width = ln.indent_width()
            kw    = ln.keyword()

            # Close every block we have dedented out of. The marker goes after the block's last body
            # line (indent greater than the block), so trailing banners / comments stay outside it.
            # Each clause of an if/elif/else or try/except/finally chain is its own block: an `elif`
            # closes the preceding `if` body (emitting a marker) and then opens a fresh frame.
            while (len(stack) > 0  and  width <= stack[-1].indent):

                frame = stack.pop()
                insertions.append((self._last_body_index(kept, i, frame.indent), frame.indent))
            #

            if (kw in BLOCK_KEYWORDS  and  self._header_end(kept, i) != -1):

                stack.append(BlockFrame(keyword=kw, indent=width))
            #
        #

        while (len(stack) > 0):

            frame = stack.pop()
            insertions.append((self._last_body_index(kept, len(kept), frame.indent), frame.indent))
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

            if (i in by_pos):

                # A preserved banner '#' just below can already serve as this block's marker; don't
                # emit a duplicate at the same indent.
                existing = self._following_markers(kept, i)
                for indent in by_pos[i]:

                    if (indent in existing):

                        existing.remove(indent)
                        continue
                    #
                    result.append(self._marker(indent))
                #
            #
        #

        return (result)
    #

    #---------------------------------------------------------------------------------------------#

    def _last_body_index(self, kept: list[Line], before: int, frame_indent: int) -> int:
        """
        Index of the block's last body line: scanning back from ``before``, the first non-blank line
        whose indent exceeds ``frame_indent``.  Trailing banners / comments sitting at or below the
        block's own indent are skipped, so the marker hugs the block, not the section separator.
        """

        fallback = -1
        j = before - 1

        while (j >= 0):

            ln = kept[j]
            if (not ln.is_blank):

                if (ln.indent_width() > frame_indent):

                    return (j)
                #
                if (fallback == -1):

                    fallback = j
                #
            #
            j -= 1
        #

        return (fallback)
    #

    def _is_banner(self, line: Line) -> bool:

        return (line.content.startswith("###"))
    #

    def _protected_markers(self, lines: list[Line]) -> set[int]:

        protected: set[int] = set()
        n = len(lines)

        for (i, ln) in enumerate(lines):

            if (ln.content != "#"):

                continue
            #

            prev_banner = (i - 1 >= 0  and  self._is_banner(lines[i - 1]))
            next_banner = (i + 1 < n   and  self._is_banner(lines[i + 1]))

            if (prev_banner  or  next_banner):

                protected.add(i)
            #
        #

        return (protected)
    #

    def _following_markers(self, kept: list[Line], i: int) -> list[int]:
        """Indent widths of the run of standalone '#' lines just after ``i`` (skipping blanks)."""

        indents: list[int] = []
        j = i + 1

        while (j < len(kept)):

            if (kept[j].is_blank):

                j += 1
                continue
            #
            if (kept[j].content == "#"):

                indents.append(kept[j].indent_width())
                j += 1
                continue
            #

            break
        #

        return (indents)
    #

    def _header_end(self, kept: list[Line], i: int) -> int:
        """
        If ``kept[i]`` opens a block, return the index of the header's last physical line (which may
        be a later continuation line for multi-line ``def`` signatures or ``if`` conditions); else
        ``-1``.  A header ends with a top-level ``:``.
        """

        j = i
        n = len(kept)
        while (j + 1 < n  and  kept[j + 1].is_continuation):

            j += 1
        #

        line             = kept[j]
        (code, _comment) = line.split_comment()
        rstripped        = code.rstrip()
        if (not rstripped.endswith(":")):

            return (-1)
        #

        shift  = len(line.indent)
        local  = [(s - shift, e - shift) for (s, e) in line.string_spans]
        masked = mask_strings(code, local)

        if (find_last_top_level(masked, ":") == len(rstripped) - 1):

            return (j)
        #

        return (-1)
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
