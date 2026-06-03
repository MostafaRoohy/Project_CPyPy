@dataclass(frozen=True)
class ParamRange:

    name    : str
    kind    : Literal['int', 'float', 'bool']
    low     : Optional[float]     = None
    high    : Optional[float]     = None
    step    : Optional[float]     = None
    choices : Optional[list[Any]] = None
#
