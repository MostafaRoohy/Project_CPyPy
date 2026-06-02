"""
Rule framework: the :class:`Rule` protocol, the shared :class:`Context`, and the registry that maps
rule names to instances together with the canonical application order.

Adding a new rule (for example a future ``operator_spacing``) is intentionally a three-line change:
write ``cpy/rule/operator_spacing.py`` exposing a ``Rule``, import it here, and register it in
:data:`_REGISTRATIONS` at the position it must run.  Nothing else in the pipeline needs to change.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from cpy.model.line import Line

#######################################################################################################
# Context + protocol
#

@dataclass
class Context:
    """Everything a rule may consult while running.  Kept small on purpose."""

    config: object | None = None
#

@runtime_checkable
class Rule(Protocol):

    name: str

    def apply(self, lines: list[Line], ctx: Context) -> list[Line]:
        ...
    #
#

#######################################################################################################
# Registry
#
# DEFAULT_ORDER is the *only* place the pipeline order is defined. Structural rules (parens) run
# before the spacing rules that depend on them; content edits run before width-sensitive alignment;
# the pure-insertion block_end_marker runs last so it never perturbs earlier grouping.
#

def _build_registry() -> tuple[dict[str, Rule], list[str]]:

    # Imported lazily to avoid a circular import at module load (rules import from base).
    from cpy.rule.typehint_spacing   import TypehintSpacing
    from cpy.rule.if_parentheses     import IfParentheses
    from cpy.rule.boolean_spacing    import BooleanSpacing
    from cpy.rule.return_parentheses import ReturnParentheses
    from cpy.rule.align_imports      import AlignImports
    from cpy.rule.align_dict_colons  import AlignDictColons
    from cpy.rule.align_assignments  import AlignAssignments
    from cpy.rule.block_end_marker   import BlockEndMarker

    ordered: list[Rule] = [
        TypehintSpacing(),
        IfParentheses(),
        BooleanSpacing(),
        ReturnParentheses(),
        AlignImports(),
        AlignDictColons(),
        AlignAssignments(),
        BlockEndMarker(),
    ]

    registry = {rule.name: rule for rule in ordered}
    order    = [rule.name for rule in ordered]

    return (registry, order)
#

_REGISTRY    : dict[str, Rule] | None = None
DEFAULT_ORDER: list[str]              = [
    "typehint_spacing",
    "if_parentheses",
    "boolean_spacing",
    "return_parentheses",
    "align_imports",
    "align_dict_colons",
    "align_assignments",
    "block_end_marker",
]

# Rules that ship enabled by default. The optional alignment / typehint rules are off until a user
# opts in, because they are the most parser-sensitive.
DEFAULT_ENABLED: list[str] = [
    "if_parentheses",
    "boolean_spacing",
    "return_parentheses",
    "align_assignments",
    "block_end_marker",
]

def get_registry() -> dict[str, Rule]:

    global _REGISTRY
    if (_REGISTRY is None):

        (_REGISTRY, _) = _build_registry()
    #

    return (_REGISTRY)
#

def get_rule(name: str) -> Rule | None:

    return (get_registry().get(name))
#
