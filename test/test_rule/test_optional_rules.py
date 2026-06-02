from conftest import run_rules

def test_align_imports():

    src = "from dataclasses import dataclass\nfrom pathlib import Path\n"
    out = "from dataclasses import dataclass\nfrom pathlib     import Path\n"
    assert run_rules(src, "align_imports") == out
#

def test_align_imports_as():

    src = "import numpy as np\nimport pandas as pd\n"
    # 'numpy' (5) is padded to 'pandas' (6) so the 'as' keywords line up.
    out = "import numpy  as np\nimport pandas as pd\n"
    assert run_rules(src, "align_imports") == out
#

def test_typehint_spacing():

    src = "def f(x : int, y: str = 'a') -> bool:\n    pass\n"
    out = "def f(x:int, y:str='a') -> bool:\n    pass\n"
    assert run_rules(src, "typehint_spacing") == out
#

def test_typehint_keeps_string_default_with_comma():

    src = 'def f(sep:str=", ") -> None:\n    pass\n'
    assert run_rules(src, "typehint_spacing") == src
#

def test_align_dict_colons():

    src = 'd = {\n    "a": 1,\n    "bbb": 2,\n}\n'
    out = 'd = {\n    "a"   : 1,\n    "bbb" : 2,\n}\n'
    assert run_rules(src, "align_dict_colons") == out
#

def test_optional_rules_idempotent():

    src = "def f(x : int) -> bool:\n    pass\n"
    once = run_rules(src, "typehint_spacing", "align_imports", "align_dict_colons")
    assert once == run_rules(once, "typehint_spacing", "align_imports", "align_dict_colons")
#
