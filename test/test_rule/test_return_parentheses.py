from conftest import run_rules

RULE = "return_parentheses"

def test_wraps_value():

    assert run_rules("def f():\n    return x\n", RULE) == "def f():\n    return (x)\n"
#

def test_bare_return_untouched():

    assert run_rules("def f():\n    return\n", RULE) == "def f():\n    return\n"
#

def test_already_wrapped_is_stable():

    assert run_rules("def f():\n    return (x)\n", RULE) == "def f():\n    return (x)\n"
#

def test_return_with_comment():

    src = "def f():\n    return x  # done\n"
    assert run_rules(src, RULE) == "def f():\n    return (x)  # done\n"
#

def test_keyword_inside_string_untouched():

    src = 'x = "return y"\n'
    assert run_rules(src, RULE) == src
#

def test_idempotent():

    src   = "def f():\n    return a + b\n"
    assert run_rules(src, RULE) == run_rules(run_rules(src, RULE), RULE)
#
