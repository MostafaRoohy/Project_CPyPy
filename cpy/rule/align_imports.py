"""
align_imports — column-align contiguous import runs (optional, off by default).

Within a maximal run of consecutive import lines at the same indent:

* ``from <module> import <names>`` lines are padded so every ``import`` keyword lines up.
* ``import <module> as <alias>`` lines are padded so every ``as`` lines up.

A blank line, comment, or non-import line breaks the run.  Each line is rebuilt from its stripped
parts, so the rule is idempotent.
"""

from __future__ import annotations

import re

from cpy.model.line import Line
from cpy.rule.base import Context

#######################################################################################################
# AlignImports
#

_FROM   = re.compile(r"^from\s+(\S+)\s+import\s+(.*)$")
_IMPORT = re.compile(r"^import\s+(\S+)\s+as\s+(.*)$")

class AlignImports:

    name = "align_imports"

    #---------------------------------------------------------------------------------------------#

    def apply(self, lines: list[Line], ctx: Context) -> list[Line]:

        group : list[Line] = []
        indent: str | None = None

        def flush() -> None:

            if (len(group) > 0):

                self._align(group)
                group.clear()
            #
        #

        for line in lines:

            if (line.is_blank  or  line.is_comment  or  line.is_continuation
                    or  line.keyword() not in ("from", "import")):

                flush()
                indent = None
                continue
            #

            if (indent is not None  and  line.indent != indent):

                flush()
            #
            indent = line.indent
            group.append(line)
        #

        flush()

        return (lines)
    #

    #---------------------------------------------------------------------------------------------#

    def _align(self, group: list[Line]) -> None:

        from_mods   = []
        import_mods = []
        for line in group:

            (code, _comment) = line.split_comment()
            m_from           = _FROM.match(code.strip())
            m_imp            = _IMPORT.match(code.strip())
            if (m_from):

                from_mods.append(len(m_from.group(1)))
            elif (m_imp):

                import_mods.append(len(m_imp.group(1)))
            #
        #

        from_w   = max(from_mods)   if from_mods   else 0
        import_w = max(import_mods) if import_mods else 0

        for line in group:

            (code, comment) = line.split_comment()
            stripped        = code.strip()
            m_from          = _FROM.match(stripped)
            m_imp           = _IMPORT.match(stripped)

            if (m_from):

                new_code = "from " + m_from.group(1).ljust(from_w) + " import " + m_from.group(2).strip()
            elif (m_imp):

                new_code = "import " + m_imp.group(1).ljust(import_w) + " as " + m_imp.group(2).strip()
            else:

                continue
            #

            rebuilt = new_code + (("  " + comment) if comment else "")
            if (rebuilt != line.content):

                line.set_content(rebuilt)
            #
        #
    #
#
