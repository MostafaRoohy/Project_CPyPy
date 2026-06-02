"""
Low-level text helpers shared by every rule.

The single most important primitive here is :func:`mask_strings`, which blanks out the characters
that live inside string literals or trailing comments while *preserving every column position*.
Rules scan and edit the masked text so they can never accidentally rewrite something inside a
string or a comment, yet the indices they compute map straight back onto the original line.
"""

from __future__ import annotations

#######################################################################################################
# Masking
#

def mask_strings(content: str, spans: list[tuple[int, int]]) -> str:
    """
    Return ``content`` with every ``[start, end)`` span replaced by spaces.

    ``spans`` are the string / comment column ranges for this physical line (as collected by the
    tokenizer in :mod:`cpy.model.line`).  The result has the exact same length as ``content`` so
    that any position found in the masked text refers to the same character in the original.
    """

    if (not spans):

        return (content)
    #

    chars = list(content)
    for (start, end) in spans:

        lo = max(0, start)
        hi = min(len(chars), end)
        for i in range(lo, hi):

            if (chars[i] != "\t"):

                chars[i] = " "
            #
        #
    #

    return ("".join(chars))
#

#######################################################################################################
# Bracket / token scanning
#

_OPEN  = "([{"
_CLOSE = ")]}"

def bracket_depth_scan(masked: str) -> list[int]:
    """
    Return a per-character list where entry ``i`` is the bracket nesting depth *before* consuming
    ``masked[i]``.  Depth never goes negative (defensive against unbalanced input).
    """

    depth  = 0
    depths = []
    for ch in masked:

        depths.append(depth)
        if (ch in _OPEN):

            depth += 1
        elif (ch in _CLOSE):

            depth = max(0, depth - 1)
        #
    #

    return (depths)
#

def is_balanced(masked: str) -> bool:
    """True when every bracket opened on this (masked) line is also closed on it."""

    depth = 0
    for ch in masked:

        if (ch in _OPEN):

            depth += 1
        elif (ch in _CLOSE):

            depth -= 1
            if (depth < 0):

                return (False)
            #
        #
    #

    return (depth == 0)
#

def find_last_top_level(masked: str, target: str) -> int:
    """
    Index of the last occurrence of single-character ``target`` that sits at bracket depth 0,
    or ``-1`` when there is none.  Used to locate the real block ``:`` past dict / lambda colons.
    """

    depths = bracket_depth_scan(masked)
    found  = -1
    for (i, ch) in enumerate(masked):

        if (ch == target  and  depths[i] == 0):

            found = i
        #
    #

    return (found)
#

def is_fully_wrapped(expr: str) -> bool:
    """
    True when ``expr`` is a single parenthesised group spanning the whole string, e.g. ``(a + b)``
    but not ``(a) + (b)``.  ``expr`` is assumed already stripped and masked-safe at the edges.
    """

    if (len(expr) < 2  or  expr[0] != "("  or  expr[-1] != ")"):

        return (False)
    #

    depth = 0
    for (i, ch) in enumerate(expr):

        if (ch == "("):

            depth += 1
        elif (ch == ")"):

            depth -= 1
            if (depth == 0  and  i != len(expr) - 1):

                # Closed the opening paren before the end -> not a single wrapping group.
                return (False)
            #
        #
    #

    return (depth == 0)
#
