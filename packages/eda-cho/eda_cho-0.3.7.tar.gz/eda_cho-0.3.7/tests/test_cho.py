from eda_cho.cli import group_by_count
import pandas as pd

def test_cho():
    result = group_by_count('올림픽', False, 4)
    assert result is not None, "something wrong"
    assert isinstance(result, pd.DataFrame), "return is not str type"
    assert len(result)==4
