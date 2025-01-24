from president_speech.db.parquet_interpreter import get_parquet_full_path
import pandas as pd
import typer

def add_keyword_count(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """
    DataFrame에 keyword_count 컬럼을 추가하여 반환합니다.
    각 speech_text에서 keyword가 등장하는 횟수를 계산합니다.
    """
    # keyword_count 컬럼 추가
    df['keyword_count'] = df['speech_text'].str.count(keyword)
    return df

def group_by_count(keyword:str, asc:bool=False, rcnt:int=12, keyword_sum:bool=False) -> pd.DataFrame:
    data_path = get_parquet_full_path()
    df = pd.read_parquet(data_path)
    fdf = df[df['speech_text'].str.contains(keyword, case=False)]
    
    if(keyword_sum):
        fdf = add_keyword_count(fdf.copy(), keyword)
        gdf = fdf.groupby("president").agg(
            count=("speech_text", "size"),  # 연설 개수
            keyword_sum=("keyword_count", "sum")  # keyword 발생 횟수 합산
        )
        sdf = gdf.sort_values(by=["keyword_sum", "count"], ascending=[asc, asc]).reset_index()
    else:
        gdf = fdf.groupby("president").size().reset_index(name="count")
        sdf = gdf.sort_values(by='count', ascending=asc).reset_index(drop=True)
    
    rdf = sdf.head(rcnt)
    return rdf

def print_group_by_count(keyword:str, asc:bool=False, rcnt:int=12, keyword_sum:bool=False):
    rdf = group_by_count(keyword, asc, rcnt,keyword_sum)
    print(rdf.to_string(index=False))
    print(f"총 합계:{len(rdf)}")
  
def entry_point():
    typer.run(print_group_by_count)









