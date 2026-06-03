from conftest import run_rules

RULE = "align_comments"

def test_aligns_trailing_comments():

    src = "a = 1  # one\nbbbb = 2  # two\n"
    out = "a = 1     # one\nbbbb = 2  # two\n"
    assert run_rules(src, RULE) == out
#

def test_blank_breaks_group():

    src = "a = 1  # one\n\nbbbb = 2  # two\n"
    # Each block aligns its own comments; the blank separates them so they stay put.
    assert run_rules(src, RULE) == src
#

def test_line_without_comment_breaks_group():

    src = "a = 1  # one\nbbbb = 2\nc = 3  # three\n"
    # 'bbbb = 2' has no comment, so the two commented lines are separate groups (each unchanged).
    assert run_rules(src, RULE) == src
#

def test_string_hash_not_a_comment():

    src = 'a = "# nope"\nbbbb = 2  # yes\n'
    # Only the second line has a real comment; the first's '#' is inside a string.
    assert run_rules(src, RULE) == src
#

def test_idempotent():

    src = "a = 1  # one\nbbbb = 2  # two\n"
    assert run_rules(src, RULE) == run_rules(run_rules(src, RULE), RULE)
#
