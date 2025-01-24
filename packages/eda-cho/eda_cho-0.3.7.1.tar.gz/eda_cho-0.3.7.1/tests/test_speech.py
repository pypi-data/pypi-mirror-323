from eda_cho.cli import group_by_count
import pandas as pd
import pytest


def test_search_exception():
    row_count = 13
    df = group_by_count(keyword="자유", asc=True, rcnt=row_count)
    
    # assert
    assert isinstance(df, pd.DataFrame)
    assert len(df) < row_count

def test_정열_및_행수제한(is_asc, president):
    row_count = 3

    df = group_by_count(keyword='자유', asc=is_asc, rcnt=row_count)
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]['president'] == president
    assert len(df) == row_count



def test_정열_및_행수제한():
    # given
    row_count = 3
    is_asc = True

    # when
    df = group_by_count(keyword="자유", asc=is_asc, rcnt=row_count)
    
    # then
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["president"] == "윤보선"
    assert len(df) == row_count

#def test_wc
    #given
    #row_count=3
    #is_asc = True

    #df=group_by_count(keyword='자유', ascend=is_asc, rowsize=row_count)

def test_default_args():

    df = group_by_count('자유')

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 12
    assert df.iloc[0]['president'] == '박정희'
    assert df.iloc[0]['count'] == 513
    assert df.iloc[1, 1] == 438


presidents_speeches = {
    "박정희": 513,
    "이승만": 438,
    "노태우": 399,
    "김대중": 305,
    "문재인": 275,
    "김영삼": 274,
    "이명박": 262,
    "전두환": 242,
    "노무현": 230,
    "박근혜": 111,
    "최규하": 14,
    "윤보선": 1
}

def test_dic():
    df = group_by_count('자유')

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 12
    for a in presidents_speeches.keys():
        president_row = df[df['president'] == a]
        assert president_row.iloc[0]['count'] == presidents_speeches[a]


def test_count_sum_check():
    df = group_by_count('자유')
    assert all(df['count'] <= df['keyword_count'])
