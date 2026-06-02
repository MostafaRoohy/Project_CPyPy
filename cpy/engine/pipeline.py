"""
The formatting pipeline: parse -> apply ordered rules -> render.

If the source cannot be tokenized (syntax error, unterminated string, …) the original text is
returned unchanged — never produce broken output.  In debug mode the pipeline runs a second pass and
asserts the result is a fixed point, catching any non-idempotent rule during development / tests.
"""

from __future__ import annotations

from cpy.config import Config
from cpy.model.line import parse
from cpy.render.renderer import render
from cpy.rule.base import Context, get_rule

#######################################################################################################
# run
#

def run(text: str, config: Config | None = None, *, debug: bool = False) -> str:

    config = config or Config()
    result = _run_once(text, config)

    if (debug):

        twice = _run_once(result, config)
        if (twice != result):

            raise AssertionError("pipeline is not idempotent for the given input")
        #
    #

    return (result)
#

def _run_once(text: str, config: Config) -> str:

    document = parse(text)

    if (not document.parse_ok):

        # Unparseable source: leave it exactly as we found it.
        return (text)
    #

    ctx   = Context(config=config)
    lines = document.lines

    for name in config.active_rules():

        rule = get_rule(name)
        if (rule is None):

            continue
        #
        lines = rule.apply(lines, ctx)
    #

    document.lines = lines

    return (render(document))
#
