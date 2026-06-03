from conftest import run_rules

RULE = "block_end_marker"

def test_marks_for_block():

    src = "for p in xs:\n    total += p\n\nmean = 0\n"
    out = "for p in xs:\n    total += p\n#\n\nmean = 0\n"
    assert run_rules(src, RULE) == out
#

def test_if_else_each_clause_marked():

    # Each clause body is closed with its own '#'.
    src = "if a:\n    x()\nelse:\n    y()\n\nz()\n"
    out = "if a:\n    x()\n#\nelse:\n    y()\n#\n\nz()\n"
    assert run_rules(src, RULE) == out
#

def test_try_except_finally_each_clause_marked():

    src = "try:\n    a()\nexcept E:\n    b()\nfinally:\n    c()\n\nd()\n"
    out = "try:\n    a()\n#\nexcept E:\n    b()\n#\nfinally:\n    c()\n#\n\nd()\n"
    assert run_rules(src, RULE) == out
#

def test_banner_marker_preserved():

    # A standalone '#' next to a '###' banner is a section separator, not a block marker.
    src = "x = 1\n#\n###############\n#\ny = 2\n"
    assert run_rules(src, RULE) == src
#

def test_multiline_if_condition_marked():

    src = "def g():\n    if (a or\n        b):\n        return c\n    return d\n"
    out = run_rules(src, RULE)
    assert "        return c\n    #\n    return d" in out
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
