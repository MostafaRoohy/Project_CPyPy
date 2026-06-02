"""
High-level formatting API — the bridge between the CLI and the pipeline.

``format_text`` is the pure function everything else builds on.  ``format_file`` / ``format_paths``
add filesystem handling (recursive ``*.py`` discovery, optional in-place writes) and report whether
each file changed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cpy.config import Config, load_config
from cpy.engine.pipeline import run

#######################################################################################################
# Result
#

@dataclass
class Result:

    path     : Path | None
    original : str
    formatted: str

    @property
    def changed(self) -> bool:

        return (self.original != self.formatted)
    #
#

#######################################################################################################
# API
#

def format_text(text: str, config: Config | None = None, *, debug: bool = False) -> str:

    return (run(text, config, debug=debug))
#

def format_file(path: str | Path, config: Config | None = None, *, write: bool = False) -> Result:

    path     = Path(path)
    original = path.read_text(encoding="utf-8")
    cfg      = config or load_config(path)
    formatted = format_text(original, cfg)

    if (write  and  formatted != original):

        path.write_text(formatted, encoding="utf-8")
    #

    return (Result(path=path, original=original, formatted=formatted))
#

def _iter_python_files(target: Path):

    if (target.is_dir()):

        yield from sorted(target.rglob("*.py"))
    else:

        yield target
    #
#

def format_paths(paths, config: Config | None = None, *, write: bool = False) -> list[Result]:

    results: list[Result] = []
    for raw in paths:

        target = Path(raw)
        for file in _iter_python_files(target):

            results.append(format_file(file, config, write=write))
        #
    #

    return (results)
#
