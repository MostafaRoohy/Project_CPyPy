"""
Configuration loading.

Config lives under ``[tool.cpy]`` in ``pyproject.toml`` (with ``[tool.CPy]`` accepted as a
fallback).  We walk up from the target path until a ``pyproject.toml`` is found.  When nothing is
found, sensible defaults apply: the five core rules on, the optional ones off.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from cpy.rule.base import DEFAULT_ENABLED, DEFAULT_ORDER

#######################################################################################################
# Config
#

@dataclass
class Config:

    enabled_rules : list[str]      = field(default_factory=lambda: list(DEFAULT_ENABLED))
    disabled_rules: list[str]      = field(default_factory=list)
    source        : Path | None    = None

    #---------------------------------------------------------------------------------------------#

    def active_rules(self) -> list[str]:
        """Enabled rules minus disabled ones, returned in the canonical pipeline order."""

        enabled = set(self.enabled_rules)
        disabled = set(self.disabled_rules)

        return ([name for name in DEFAULT_ORDER if (name in enabled  and  name not in disabled)])
    #
#

#######################################################################################################
# Loading
#

def _find_pyproject(start: Path) -> Path | None:

    start = start.resolve()
    candidates = [start, *start.parents] if start.is_dir() else [start.parent, *start.parent.parents]

    for directory in candidates:

        candidate = directory / "pyproject.toml"
        if (candidate.is_file()):

            return (candidate)
        #
    #

    return (None)
#

def load_config(start_path: str | Path | None = None) -> Config:

    start = Path(start_path) if start_path else Path.cwd()

    # An explicit path straight to a .toml file is loaded directly; anything else is treated as a
    # location to start discovery from (walk up looking for pyproject.toml).
    if (start.is_file()  and  start.suffix == ".toml"):

        pyproject = start
    else:

        pyproject = _find_pyproject(start)
    #

    if (pyproject is None):

        return (Config())
    #

    try:

        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):

        return (Config())
    #

    tool    = data.get("tool", {})
    section = tool.get("cpy")  or  tool.get("CPy")  or  {}

    return (Config(
        enabled_rules  = list(section.get("enabled_rules", DEFAULT_ENABLED)),
        disabled_rules = list(section.get("disabled_rules", [])),
        source         = pyproject,
    ))
#
