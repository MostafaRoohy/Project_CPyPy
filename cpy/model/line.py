"""
Internal source model.

A :class:`Document` is the parsed form of a source file: a list of :class:`Line` objects plus the
metadata rules need to stay safe (which column ranges are strings / comments, and which physical
lines are bracket / backslash continuations).  The metadata is computed *once* with the stdlib
``tokenize`` module and then cached on each line, so individual rules never re-parse.
"""

from __future__ import annotations

import io
import tokenize
from dataclasses import dataclass, field

# f-string tokens only exist on Python 3.12+. On 3.11 an f-string is a single STRING token.
# Comments are tracked separately (see comment_col) so that splitting a trailing comment can still
# locate the real '#' after string contents have been masked away.
_STRING_TOKEN_TYPES = frozenset(
    t for t in (
        tokenize.STRING,
        getattr(tokenize, "FSTRING_START", None),
        getattr(tokenize, "FSTRING_MIDDLE", None),
        getattr(tokenize, "FSTRING_END", None),
    )
    if t is not None
)

#######################################################################################################
# Keywords that open an indented block (used by block_end_marker and header detection)
#

BLOCK_KEYWORDS = frozenset({
    "if", "elif", "else",
    "for", "while",
    "def", "class",
    "try", "except", "finally",
    "with",
})

CONDITION_KEYWORDS = frozenset({"if", "elif", "while", "assert"})

#######################################################################################################
# Line
#

@dataclass
class Line:
    """One physical source line and the cached facts a rule may need about it."""

    raw            : str
    indent         : str
    content        : str
    is_blank       : bool
    is_comment     : bool
    is_continuation: bool
    string_spans   : list[tuple[int, int]] = field(default_factory=list)
    comment_col    : int | None            = None

    #---------------------------------------------------------------------------------------------#

    def indent_width(self) -> int:

        return (len(self.indent))
    #

    def keyword(self) -> str | None:
        """First bare-word token of the line, or ``None`` for blanks / comments / non-words."""

        if (self.is_blank  or  self.is_comment):

            return (None)
        #

        token = ""
        for ch in self.content:

            if (ch.isalnum()  or  ch == "_"):

                token += ch
            else:

                break
            #
        #

        return (token or None)
    #

    def split_comment(self) -> tuple[str, str]:
        """Split ``content`` into ``(code, comment)`` using the tokenizer-located comment column."""

        if (self.comment_col is None):

            return (self.content, "")
        #

        col = self.comment_col - len(self.indent)
        if (col < 0  or  col > len(self.content)):

            return (self.content, "")
        #

        # Pull whitespace that preceded the '#' into the comment part so it round-trips verbatim.
        code_end = col
        while (code_end > 0  and  self.content[code_end - 1] in " \t"):

            code_end -= 1
        #

        return (self.content[:code_end], self.content[col:])
    #

    def set_content(self, new_content: str) -> None:
        """Replace the code part of the line, refreshing string/comment metadata to match."""

        self.content = new_content
        self.raw     = self.indent + new_content

        # The original tokenizer-derived spans/comment column are now stale; rescan this single line
        # so a later rule that re-splits it sees correct offsets.
        (spans, comment_col) = scan_line_metadata(self.raw)
        self.string_spans     = spans
        self.comment_col      = comment_col
    #
#

#######################################################################################################
# Single-line rescan (keeps metadata fresh after edits)
#

def scan_line_metadata(raw: str) -> tuple[list[tuple[int, int]], int | None]:
    """
    Scan one physical line for string spans and the first real comment column.

    Used to refresh :class:`Line` metadata after an edit (the file-level tokenizer ran only on the
    original text).  Handles single/triple quotes and backslash escapes; the first ``#`` outside a
    string starts the comment.
    """

    spans       : list[tuple[int, int]] = []
    comment_col : int | None            = None
    i           = 0
    n           = len(raw)
    in_string   = False
    quote       = ""
    start       = 0

    while (i < n):

        ch = raw[i]

        if (in_string):

            if (ch == "\\"):

                i += 2
                continue
            #
            if (raw[i:i + len(quote)] == quote):

                i += len(quote)
                spans.append((start, i))
                in_string = False
                quote     = ""
                continue
            #
            i += 1
            continue
        #

        if (ch == "#"):

            comment_col = i
            break
        #
        if (ch in "\"'"):

            quote     = (ch * 3) if (raw[i:i + 3] == ch * 3) else ch
            in_string = True
            start     = i
            i        += len(quote)
            continue
        #

        i += 1
    #

    if (in_string):

        spans.append((start, n))
    #

    return (spans, comment_col)
#

#######################################################################################################
# Document
#

@dataclass
class Document:

    lines           : list[Line]
    newline         : str
    trailing_newline: bool
    parse_ok        : bool
#

#######################################################################################################
# Parsing
#

def _detect_newline(text: str) -> str:

    if ("\r\n" in text):

        return ("\r\n")
    #

    return ("\n")
#

def _collect_metadata(text: str) -> tuple[dict[int, list[tuple[int, int]]], set[int], bool]:
    """
    Run ``tokenize`` once over ``text``.

    Returns ``(spans_by_line, comment_cols, ok)`` where ``spans_by_line`` maps a 1-based physical
    line number to the *string* column ranges on it, ``comment_cols`` maps a line number to the
    starting column of its trailing ``#`` comment (kept separate from strings so the comment is not
    masked away), and ``ok`` is False when tokenizing failed (caller then leaves the file untouched).
    """

    spans_by_line : dict[int, list[tuple[int, int]]] = {}
    comment_cols  : dict[int, int]                    = {}

    try:

        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):

        return ({}, {}, False)
    #

    for tok in tokens:

        (srow, scol) = tok.start
        (erow, ecol) = tok.end

        if (tok.type in _STRING_TOKEN_TYPES):

            # Record the span on each physical line the token covers.
            if (srow == erow):

                spans_by_line.setdefault(srow, []).append((scol, ecol))
            else:

                # Multi-line string: blank the tail of the first line, all of the middle lines,
                # and the head of the last line.
                spans_by_line.setdefault(srow, []).append((scol, 10**6))
                for row in range(srow + 1, erow):

                    spans_by_line.setdefault(row, []).append((0, 10**6))
                #
                spans_by_line.setdefault(erow, []).append((0, ecol))
            #
        elif (tok.type == tokenize.COMMENT):

            comment_cols[srow] = scol
        #
    #

    return (spans_by_line, comment_cols, True)
#

def _continuation_lines(text: str, newline: str) -> set[int]:
    """
    Determine, robustly, which 1-based physical lines are continuations of a previous logical line
    (inside open brackets or after a backslash).  Computed independently of token bookkeeping by
    tracking bracket depth and backslash continuations across the file.
    """

    raw_lines = text.split(newline)
    cont      : set[int] = set()

    # Build per-line masks lazily via tokenize spans would be circular; instead do a light scan that
    # ignores brackets inside strings by using a simple string-state machine.
    depth          = 0
    prev_backslash = False
    in_string      = False
    string_quote   = ""

    for (idx, line) in enumerate(raw_lines, start=1):

        if (depth > 0  or  prev_backslash):

            cont.add(idx)
        #

        i = 0
        prev_backslash = False
        while (i < len(line)):

            ch = line[i]

            if (in_string):

                if (ch == "\\"):

                    i += 2
                    continue
                #
                if (line[i:i + len(string_quote)] == string_quote):

                    in_string    = False
                    i           += len(string_quote)
                    string_quote = ""
                    continue
                #
                i += 1
                continue
            #

            if (ch == "#"):

                break
            #

            if (ch in "\"'"):

                triple = line[i:i + 3]
                if (triple == ch * 3):

                    string_quote = ch * 3
                    in_string    = True
                    i           += 3
                    continue
                #
                # Single-line quote: find its close on the same line; if unclosed, treat as opening.
                string_quote = ch
                in_string    = True
                i           += 1
                continue
            #

            if (ch in "([{"):

                depth += 1
            elif (ch in ")]}"):

                depth = max(0, depth - 1)
            #

            i += 1
        #

        if (line.endswith("\\")  and  not in_string):

            prev_backslash = True
        #

        # A single-line string never carries to the next line; reset unless it was triple-quoted.
        if (in_string  and  len(string_quote) == 1):

            in_string    = False
            string_quote = ""
        #
    #

    return (cont)
#

def parse(text: str) -> Document:
    """Parse ``text`` into a :class:`Document`.  Never raises; sets ``parse_ok=False`` on failure."""

    newline          = _detect_newline(text)
    trailing_newline = text.endswith("\n")

    # Normalise to '\n' internally for splitting; remember the real newline for rendering.
    normalised = text.replace("\r\n", "\n")
    raw_lines  = normalised.split("\n")

    # split() leaves a trailing "" when the text ends in a newline; drop it, we re-add on render.
    if (trailing_newline  and  raw_lines  and  raw_lines[-1] == ""):

        raw_lines = raw_lines[:-1]
    #

    (spans_by_line, comment_cols, ok) = _collect_metadata(normalised)
    cont_lines                        = _continuation_lines(normalised, "\n")

    lines: list[Line] = []
    for (idx, raw) in enumerate(raw_lines, start=1):

        stripped = raw.lstrip(" \t")
        indent   = raw[:len(raw) - len(stripped)]
        spans    = spans_by_line.get(idx, [])

        lines.append(Line(
            raw             = raw,
            indent          = indent,
            content         = stripped,
            is_blank        = (stripped == ""),
            is_comment      = stripped.startswith("#"),
            is_continuation = (idx in cont_lines),
            string_spans    = spans,
            comment_col     = comment_cols.get(idx),
        ))
    #

    return (Document(
        lines            = lines,
        newline          = newline,
        trailing_newline = trailing_newline,
        parse_ok         = ok,
    ))
#
