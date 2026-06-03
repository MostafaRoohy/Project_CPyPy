from conftest import run_rules

RULE = "blank_after_header"

def test_blank_after_def():

    assert run_rules("def f():\n    return 1\n", RULE) == "def f():\n\n    return 1\n"
#

def test_blank_after_class():

    assert run_rules("class C:\n    x = 1\n", RULE) == "class C:\n\n    x = 1\n"
#

def test_blank_before_docstring():

    src = 'class C:\n    """doc"""\n'
    assert run_rules(src, RULE) == 'class C:\n\n    """doc"""\n'
#

def test_async_def():

    assert run_rules("async def f():\n    pass\n", RULE) == "async def f():\n\n    pass\n"
#

def test_existing_blank_not_duplicated():

    src = "def f():\n\n    return 1\n"
    assert run_rules(src, RULE) == src
#

def test_one_liner_untouched():

    assert run_rules("class X: pass\n", RULE) == "class X: pass\n"
#

def test_multiline_signature():

    src = "def f(a,\n      b):\n    return a\n"
    out = "def f(a,\n      b):\n\n    return a\n"
    assert run_rules(src, RULE) == out
#

def test_idempotent():

    src = "class C:\n    def m(self):\n        return 1\n"
    assert run_rules(src, RULE) == run_rules(run_rules(src, RULE), RULE)
#
