from eda_ji.cli import group_by_count
import pandas as pd
import pytest
    
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

def test_search():
    row_count = 13
    # When
    df = group_by_count(keyword="자유", asc=True, rcnt=row_count)
    # assert
    assert isinstance(df, pd.DataFrame) 
    assert len(df) < row_count

def test_noascen():
    row_count = 3
    is_asc = True
    # When
    df = group_by_count(keyword="자유", asc=is_asc, rcnt=row_count)
    # assert
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["president"] == "윤보선"
    assert len(df) == row_count

def test_ascen():
    row_count = 3
    is_asc = False
    # When
    df = group_by_count(keyword="자유", asc=is_asc, rcnt=row_count)
    # assert
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["president"] == "박정희"
    assert len(df) == row_count

@pytest.mark.parametrize("is_asc, president", [(True,"윤보선"),(False,"박정희")])
def test_sort(is_asc,president):
    row_count = 3

    # When
    df = group_by_count(keyword="자유", asc=is_asc, rcnt=row_count)
    
    # assert
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["president"] == president
    assert len(df) == row_count

def test_all_count():
    # When
    df = group_by_count("자유") 
    presidents_speeches = {}
    for i in range(len(df)):
        presidents_speeches[df.iloc[i]["president"]] = df.iloc[i]["count"]
        #assert president_row.iloc[i]["count"] == s_count
    # assert
    assert presidents_speeches["박정희"] == 513 
    assert presidents_speeches["이승만"] == 438 
    assert presidents_speeches["노태우"] == 399 
    assert presidents_speeches["김대중"] == 305 
    assert presidents_speeches["문재인"] == 275
    assert presidents_speeches["김영삼"] == 274 
    assert presidents_speeches["이명박"] == 262 
    assert presidents_speeches["전두환"] == 242 
    assert presidents_speeches["노무현"] == 230 
    assert presidents_speeches["박근혜"] == 111 
    assert presidents_speeches["최규하"] == 14 
    assert presidents_speeches["윤보선"] == 1 
    

def test_all_count_keyword_sum():
    # given
    # global dict
    
    # when
    df = group_by_count("자유", keyword_sum = True)
    
    # assert
    assert isinstance(df, pd.DataFrame)
    assert "keyword_sum" in df.columns
    # count 보다 keyword_sum이 크거나 같음을 확인 assert
    # 1 - 모범 case 
    assert all (df["count"] <= df["keyword_sum"])  # 모든 값이 다 True인지 알려주는 내장함수 all(데이터 프레임 요소별로 비교함)
    # 2
    for row in df.itertuples():
        assert row.keyword_sum >= row.count
    # 3!!!
    for i in range(len(df)):
        keyword_sum = df.iloc[i, df.columns.get_loc("keyword_sum")]
        count = df.iloc[i, df.columns.get_loc("count")]
        assert keyword_sum >= count


