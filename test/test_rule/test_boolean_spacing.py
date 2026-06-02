from conftest import run_rules

RULE = "boolean_spacing"

def test_double_spaces_and_or():

    src = "if a and b or c:\n    pass\n"
    assert run_rules(src, RULE) == "if a  and  b  or  c:\n    pass\n"
#

def test_collapses_existing_extra_spaces():

    src = "if a   and   b:\n    pass\n"
    assert run_rules(src, RULE) == "if a  and  b:\n    pass\n"
#

def test_substrings_untouched():

    src = "if brand or order:\n    pass\n"
    # 'brand' and 'order' must not be touched; only the standalone 'or' is.
    assert run_rules(src, RULE) == "if brand  or  order:\n    pass\n"
#

def test_inside_string_untouched():

    src = 'if x == "a and b":\n    pass\n'
    assert run_rules(src, RULE) == src
#

def test_non_condition_line_untouched():

    src = "x = a and b\n"
    assert run_rules(src, RULE) == src
#

def test_idempotent():

    src = "while a and b and c:\n    pass\n"
    assert run_rules(src, RULE) == run_rules(run_rules(src, RULE), RULE)
#
