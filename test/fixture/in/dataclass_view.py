@dataclass(slots=True)
class OHLCVView:
    ser_timestamp : pd.Series  # float64
    ser_open : pd.Series  # float64
    ser_close : pd.Series  # float64

    arr_timestamp : np.ndarray  # float64
    arr_open : np.ndarray  # float64
    arr_close : np.ndarray  # float64
