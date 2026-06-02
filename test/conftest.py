"""
Shared test helpers.

``run_rules`` formats a snippet through the pipeline with an explicit set of rules enabled, so each
test exercises exactly the rule it is about (and we can still assert idempotence of the full thing).
"""

from __future__ import annotations

from cpy.config import Config
from cpy.engine.pipeline import run

def run_rules(text: str, *rules: str) -> str:

    config = Config(enabled_rules=list(rules), disabled_rules=[])

    return (run(text, config, debug=True))
#
