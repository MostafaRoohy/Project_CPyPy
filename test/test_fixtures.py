"""
Golden-file tests: every ``test/fixture/in/<name>.py`` must format to ``test/fixture/out/<name>.py``,
and the expected output must already be a fixed point (formatting it again changes nothing).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cpy.config import Config
from cpy.engine.pipeline import run
from cpy.rule.base import DEFAULT_ENABLED

FIXTURE_DIR = Path(__file__).parent / "fixture"
CASES       = sorted((FIXTURE_DIR / "in").glob("*.py"))

@pytest.mark.parametrize("infile", CASES, ids=[c.stem for c in CASES])
def test_fixture(infile: Path):

    expected = (FIXTURE_DIR / "out" / infile.name).read_text(encoding="utf-8")
    config   = Config(enabled_rules=list(DEFAULT_ENABLED))

    formatted = run(infile.read_text(encoding="utf-8"), config)

    assert formatted == expected
    assert run(expected, config) == expected      # expected output is itself stable
#
