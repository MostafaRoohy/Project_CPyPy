from conftest import run_rules

RULE = "align_annotations"

def test_align_colon_only():

    src = "name : str\nkind : int\n"
    assert run_rules(src, RULE) == "name : str\nkind : int\n"
#

def test_align_colon_padding():

    src = "name : str\nchoices : int\n"
    out = "name    : str\nchoices : int\n"
    assert run_rules(src, RULE) == out
#

def test_align_colon_and_default():

    src = "name : str\nlow : Optional[float] = None\nhigh : Optional[float] = None\n"
    out = (
        "name : str\n"
        "low  : Optional[float] = None\n"
        "high : Optional[float] = None\n"
    )
    assert run_rules(src, RULE) == out
#

def test_dotted_target():

    src = "self.a : int = 1\nself.bb : str = 'x'\n"
    out = "self.a  : int = 1\nself.bb : str = 'x'\n"
    assert run_rules(src, RULE) == out
#

def test_spans_blank_line():

    src = "a : int\nbb : int\n\nccc : int\n"
    out = "a   : int\nbb  : int\n\nccc : int\n"
    assert run_rules(src, RULE) == out
#

def test_block_header_not_touched():

    src = "if x:\n    pass\n"
    assert run_rules(src, RULE) == src
#

def test_plain_assignment_not_touched():

    src = "x = 1\n"
    assert run_rules(src, RULE) == src
#

def test_dict_colon_not_mistaken():

    # The ':' is inside braces (depth > 0), so this is not an annotation.
    src = "d = {1: 2}\n"
    assert run_rules(src, RULE) == src
#

def test_idempotent():

    src = "a : int = 1\nbbb : int = 2\n"
    assert run_rules(src, RULE) == run_rules(run_rules(src, RULE), RULE)
#
