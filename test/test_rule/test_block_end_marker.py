from conftest import run_rules

RULE = "block_end_marker"

def test_marks_for_block():

    src = "for p in xs:\n    total += p\n\nmean = 0\n"
    out = "for p in xs:\n    total += p\n#\n\nmean = 0\n"
    assert run_rules(src, RULE) == out
#

def test_if_else_chain_marked_once():

    src = "if a:\n    x()\nelse:\n    y()\n\nz()\n"
    out = "if a:\n    x()\nelse:\n    y()\n#\n\nz()\n"
    assert run_rules(src, RULE) == out
#

def test_nested_blocks_emit_inner_then_outer():

    src = "def f():\n    for x in y:\n        a()\n    return\n"
    out = "def f():\n    for x in y:\n        a()\n    #\n    return\n#\n"
    assert run_rules(src, RULE) == out
#

def test_banner_lines_survive():

    src = "####\nx = 1\n"
    # A multi-hash banner is not a structural marker and must not be removed.
    assert "####" in run_rules(src, RULE)
#

def test_real_comment_survives():

    src = "def f():\n    pass  # note\n"
    assert "# note" in run_rules(src, RULE)
#

def test_idempotent():

    src = "for p in xs:\n    total += p\n\nmean = 0\n"
    assert run_rules(src, RULE) == run_rules(run_rules(src, RULE), RULE)
#
