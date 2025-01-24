from cob_eda.cli import group_by_count
from cob_eda.cli import group_by_count_akc
import pandas as pd
import pytest


def test1():
    df=group_by_count("경제",False,5)
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["president"] == "문재인"
    assert len(df) == 5

def test_search_exception():
    # 주어진변수
    row_count = 13
    df = group_by_count(keyword="자유", asorde=True, howmany=row_count)
    
    # assert
    assert isinstance(df, pd.DataFrame)
    assert len(df) < row_count

def test_정열_및_행수제한():
    # given
    row_count = 3
    is_asc = True

    # when
    df = group_by_count(keyword="자유", asorde=is_asc, howmany=row_count)
    
    # then
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["president"] == "윤보선"
    assert len(df) == row_count

@pytest.mark.parametrize("asc,president",[(True,"윤보선"),(False,"박정희")])
def test_정열_및_행수제한(asc,president):
    # given
    rc = 3
    #asc = True

    # when
    df = group_by_count("자유",asorde=asc,howmany=rc)

    # then
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["president"] == president
    #assert df.iloc[0]["count"]==1
    assert df.iloc[0]["president"] == president
    assert len(df) ==3
    #assert df.iloc[0]["count"]==513
    #assert df.iloc[1]["count"]==438

def test_딕셔너리확인():
    
    df = group_by_count("자유",False,12)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 12
    presidents_speeche = {}
    for i in range(len(df)):
        presidents_speeche[df.iloc[i]["president"]]=df.iloc[i]["count"]
    for i,v in presidents_speeche.items():
        assert presidents_speeche[i]==v
    
    assert presidents_speeche["박정희"]==513
    assert presidents_speeche["이승만"]==438
    assert presidents_speeche["윤보선"]==1


presidents_speeche = { "박정희": 513,"이승만": 438,"노태우": 399,"김대중": 305,"문재인": 275,"김영삼": 274,"이명박": 262,"전두환": 242,"노무현": 230,"박근혜": 111,"최규하": 14,"윤보선": 1 }


def test_all_count():
    #given
    #global presidents_speeche

    #when
    df = group_by_count("자유",False,12)

    #then
    assert isinstance(df,pd.DataFrame)
    assert len(df) == 12

    for p_name,s_count in presidents_speeche.items():
        president_row = df[df["president"] == p_name]
        assert president_row.iloc[0]["count"]== s_count


def test_all_count_enum_iat():
    #given
    #global presidents_speeche

    #when
    df = group_by_count("자유",False,12)

    #then
    assert isinstance(df,pd.DataFrame)
    assert len(df) == 12

    for i,(p_name,s_count) in enumerate(presidents_speeche.items()):
        assert df.iat[i,1] == s_count




def test_all_count_keywordsum():
    # given
    # global dict

    # when
    df = group_by_count_akc(keyword="자유",
                        keyword_sum=True
                        )
    
    # then
    assert isinstance(df, pd.DataFrame)
    assert "keyword_sum" in df.columns

    # TRY - keyword_sum 이 count 보다 항상 크거나 같음
    # 1
    assert all(df["keyword_sum"] >= df["count"])
    # 모든 쌍 컬럼 쌍으로 비교 , all- 내장함수임 각 쌍들의 비교가 assert 한대로 맞다면 True 리턴 아님 False 
    # 2
    for row in df.itertuples():
        assert row.keyword_sum >= row.count

    # 3 - 열의 순서를 알고 있고 위치 기반으로 다루고 싶을 때.
    for i in range(len(df)):
        keyword_sum = df.iloc[i, df.columns.get_loc("keyword_sum")]
        count = df.iloc[i, df.columns.get_loc("count")]
        assert keyword_sum >= count

    # 4
    for i in range(len(df)):
        keyword_sum = df.loc[i, "keyword_sum"]
        count = df.loc[i, "count"]
        assert keyword_sum >= count

    # 4
    for i in range(len(df)):
        keyword_sum = df.iat[i, 2]  # 첫 번째 열 (0번 인덱스)
        count = df.iat[i, 1]        # 두 번째 열 (1번 인덱스)
        assert keyword_sum >= count
