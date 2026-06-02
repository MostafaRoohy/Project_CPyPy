"""
Render the internal model back to source text.

Rules mutate ``Line.raw``; rendering simply joins those raw lines with the document's detected
newline style and enforces a single trailing newline so ``check`` never reports phantom changes.
"""

from __future__ import annotations

from cpy.model.line import Document

#######################################################################################################
# render
#

def render(document: Document) -> str:

    body = document.newline.join(line.raw for line in document.lines)

    if (document.trailing_newline):

        body += document.newline
    #

    return (body)
#
