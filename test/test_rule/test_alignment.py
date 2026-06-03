from conftest import run_rules

RULE = "align_assignments"

def test_aligns_group():

    src = "n = 1\ntotal = 0\ncount = 0\n"
    out = "n     = 1\ntotal = 0\ncount = 0\n"
    assert run_rules(src, RULE) == out
#

def test_blank_line_spans_group():

    # Alignment spans blank lines within the same indent block: all four share one column.
    src = "a = 1\nbb = 2\n\nc = 3\nddd = 4\n"
    out = "a   = 1\nbb  = 2\n\nc   = 3\nddd = 4\n"
    assert run_rules(src, RULE) == out
#

def test_comment_line_breaks_group():

    src = "a = 1\nbb = 2\n# note\nc = 3\nddd = 4\n"
    out = "a  = 1\nbb = 2\n# note\nc   = 3\nddd = 4\n"
    assert run_rules(src, RULE) == out
#

def test_annotated_line_left_to_align_annotations():

    # align_assignments must NOT touch an annotated assignment (that is align_annotations' job).
    src = "x : int = 5\n"
    assert run_rules(src, RULE) == src
#

def test_comparison_not_aligned():

    src = "a == b\nc = d\n"
    # '==' is not an assignment; only the second line normalises.
    assert run_rules(src, RULE) == "a == b\nc = d\n"
#

def test_augmented_assignment_breaks_group():

    src = "total = 0\ntotal += p\ncount = 0\n"
    out = "total = 0\ntotal += p\ncount = 0\n"
    assert run_rules(src, RULE) == out
#

def test_kwarg_equals_not_aligned():

    src = "result = compute(fee=0.01, rate=0.02)\n"
    assert run_rules(src, RULE) == src
#

def test_tuple_unpack_aligns_on_equals():

    src = "a, b = 1, 2\nxx = 3\n"
    out = "a, b = 1, 2\nxx   = 3\n"
    assert run_rules(src, RULE) == out
#

def test_indent_change_breaks_group():

    src = "x = 1\nif y:\n    aa = 2\n    b = 3\n"
    out = "x = 1\nif y:\n    aa = 2\n    b  = 3\n"
    assert run_rules(src, RULE) == out
#

def test_idempotent():

    src = "n = 1\ntotal = 0\ncount = 0\n"
    assert run_rules(src, RULE) == run_rules(run_rules(src, RULE), RULE)
#
