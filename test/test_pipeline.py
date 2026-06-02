"""Full-pipeline behaviour: end-to-end formatting, idempotence, and safety on broken input."""

from __future__ import annotations

import subprocess
import sys

from conftest import run_rules

from cpy.config import Config
from cpy.engine.pipeline import run

ALL_CORE = ("if_parentheses", "boolean_spacing", "return_parentheses",
            "align_assignments", "block_end_marker")

#######################################################################################################

def test_end_to_end_core_style():

    src = (
        "def f(prices):\n"
        "    n = len(prices)\n"
        "    total = 0.0\n"
        "    if n > 0 and total < 10:\n"
        "        return total\n"
    )
    out = run_rules(src, *ALL_CORE)

    assert "n     = len(prices)" in out
    assert "if (n > 0  and  total < 10):" in out
    assert "return (total)" in out
    assert out.rstrip().endswith("#")
#

def test_pipeline_is_idempotent():

    src = (
        "def f(prices):\n"
        "    n = len(prices)\n"
        "    total = 0.0\n"
        "    for p in prices:\n"
        "        total += p\n"
        "    if n > 0 and total < 10:\n"
        "        return total\n"
        "    return 0\n"
    )
    once  = run_rules(src, *ALL_CORE)
    twice = run_rules(once, *ALL_CORE)
    assert once == twice
#

def test_syntax_error_left_unchanged():

    broken = "def f(:\n    return\n"
    assert run(broken, Config(enabled_rules=list(ALL_CORE))) == broken
#

def test_crlf_newlines_preserved():

    src = "x = 1\r\ny = 2\r\n"
    out = run(src, Config(enabled_rules=["align_assignments"]))
    assert "\r\n" in out
    assert "\n\n" not in out.replace("\r\n", "")
#

def test_cli_stdin_roundtrip():

    src    = "def f():\n    return x\n"
    result = subprocess.run(
        [sys.executable, "-m", "cpy", "format", "-"],
        input=src, capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "return (x)" in result.stdout
#

def test_cli_check_exit_code():

    dirty = subprocess.run(
        [sys.executable, "-m", "cpy", "check", "-"],
        input="def f():\n    return x\n", capture_output=True, text=True,
    )
    assert dirty.returncode == 1

    clean = subprocess.run(
        [sys.executable, "-m", "cpy", "check", "-"],
        input="x = 1\n", capture_output=True, text=True,
    )
    assert clean.returncode == 0
#
