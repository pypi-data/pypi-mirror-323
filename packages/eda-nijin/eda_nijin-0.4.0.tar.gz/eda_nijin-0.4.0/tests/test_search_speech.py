from eda_nijin.cli import group_by_count
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

def test_search_exception():
    row_count = 13
    df = group_by_count(keyword="자유", asc=True, rcnt=row_count)

    #assert
    assert isinstance(df, pd.DataFrame)
    assert len(df) < row_count

@pytest.mark.parametrize("is_asc, president", [(True,"윤보선"), (False, "박정희")])
def test_sort(is_asc, president):
    #given
    row_count = 3
    #is_asc = True

    #when
    df = group_by_count(keyword = "자유", asc=is_asc, rcnt=row_count)
    
    #then 
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["president"] == president
    assert len(df) == row_count 

def test_default_args():
    #given 
    row_count = 3
    is_asc = False

    #when
    df = group_by_count(keyword = "자유")

    #then
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 12
    assert df.iloc[0]["president"] == "박정희"
    assert df.iloc[0]["count"] == 513
    assert df.iloc[1]["count"] == 438
    assert df.iloc[11]["count"] == 1
  
def test_all_count():
    #given
    #global

    #when
    df = group_by_count("자유")
   
   #then
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 12

    for p_name, s_count in presidents_speeches.items():
        president_row = df[df["president"] == p_name]
        assert president_row.iloc[0]["count"] == s_count

def test_all_count_iat():
    #given
    #global

    #when
    df = group_by_count("자유")

   #then
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 12

    for i, (p_name, s_count) in enumerate(presidents_speeches.items()):
        assert df.iat[i,1] == s_count

def test_all_count_Keyword_sum():
    #given
    #global dict

    #when
    df = group_by_count(keyword="자유",
                        keyword_sum=True
                        )
    
    #then
    assert isinstance(df, pd.DataFrame)
    assert "keyword_sum" in df.columns
    #count 보다 keyword_sum이 크거나 같음을 확인 assert
    # 1
    assert all(df["keyword_sum"] >= df["count"])

    # 2 
    for row in df.itertuples():
        assert row.keyword_sum >= row.count

    # 3
    for i in range(len(df)):
        keyword_sum = df.iloc[i,df.columns.get_loc("keyword_sum")]
        count = df.iloc[i, df.columns.get_loc("count")]
        assert keyword_sum >= count

    # 4
    for i in range(len(df)):
        keyword_sum = df.loc[i, "keyword_sum"]
        count = df.loc[i, "count"]
        assert keyword_sum >= count

    #5
    for i in range(len(df)):
        keyword_sum = df.iat[i,2]
        count = df.iat[i,1]
        assert keyword_sum >= count







