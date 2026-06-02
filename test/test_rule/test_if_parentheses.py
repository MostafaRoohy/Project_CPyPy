from conftest import run_rules

RULE = "if_parentheses"

def test_wraps_if():

    assert run_rules("if x > 0:\n    pass\n", RULE) == "if (x > 0):\n    pass\n"
#

def test_wraps_elif_and_while():

    assert run_rules("while x:\n    pass\n", RULE) == "while (x):\n    pass\n"
    src = "if a:\n    pass\nelif b:\n    pass\n"
    assert run_rules(src, RULE) == "if (a):\n    pass\nelif (b):\n    pass\n"
#

def test_for_is_untouched():

    assert run_rules("for x in y:\n    pass\n", RULE) == "for x in y:\n    pass\n"
#

def test_already_wrapped_is_stable():

    assert run_rules("if (x > 0):\n    pass\n", RULE) == "if (x > 0):\n    pass\n"
#

def test_dict_colon_in_condition_not_mistaken_for_block_colon():

    src = 'if d["a"] == 1:\n    pass\n'
    assert run_rules(src, RULE) == 'if (d["a"] == 1):\n    pass\n'
#

def test_keyword_inside_string_untouched():

    src = 'x = "if y:"\n'
    assert run_rules(src, RULE) == src
#

def test_idempotent():

    src   = "if x > 0 and y < 10:\n    pass\n"
    once  = run_rules(src, RULE)
    twice = run_rules(once, RULE)
    assert once == twice
#
