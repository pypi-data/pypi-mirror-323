from president_speech.db.parquet_interpreter import get_parquet_full_path
import pandas as pd
import typer
from typing import Dict

def add_keyword_count(keyword: str, asc: bool=False, rcnt: int=10, keyword_sum: bool=True) -> pd.DataFrame:
    # 데이터 받아오기
    data_path = get_parquet_full_path()
    df = pd.read_parquet(data_path)
    
    # 'speech_text' 열에서 `keyword`가 포함되어 있으면 1, 아니면 0을 `is_contained'열에 추가`
    df['is_contained'] = df['speech_text'].str.contains(keyword, case=False).astype(int)
    
    # 'speech_text' 열에서 `keyword`가 포함되어 있으면 포함된 수만큼의 값을 'keyword_count'열에 추가
    df['keyword_count'] = df['speech_text'].str.count(keyword)

    # 'keyword'가 포함된 행과 얼마만큼 포함되었는지의 행을 합쳐 대통령 별로 그룹화
    # count: `keyword`가 한 번이라도 등장한 행의 수
    # keyword_sum: `keyword`의 총 등장 횟수
    gdf = df.groupby('president').agg(
        count=('is_contained', 'sum'),
        keyword_sum=('keyword_count', 'sum')
    ).reset_index()

    # 'count'를 기준으로 정렬하고, rcnt만큼의 데이터만 위에서 부터 가져옴
    sdf = gdf.sort_values(by='count', ascending=asc).head(rcnt).reset_index(drop=True)
    
    if not keyword_sum:
        sdf = sdf[['president', 'count']]
    
    return sdf

def group_by_count(keyword: str, asc: bool=False, rcnt: int=12) -> pd.DataFrame:
    data_path = get_parquet_full_path()
    df = pd.read_parquet(data_path)
    f_df = df[df['speech_text'].str.contains(keyword, case=False)]

    if f_df.empty:
        return None

    rdf = f_df.groupby('president').size().reset_index(name='count')
    sdf = rdf.sort_values(by='count', ascending=asc).reset_index(drop=True)
    cdf = sdf.head(rcnt)
    
    return cdf

def group_by_count_to_dict(keyword: str, asc: bool=False, rcnt: int=12) -> Dict[str, int]:
    data_path = get_parquet_full_path()
    df = pd.read_parquet(data_path)
    fdf = df[df['speech_text'].str.contains(keyword, case=False)]
    rdf = fdf.groupby('president').size().reset_index(name='count')
    sdf = rdf.sort_values(by='count', ascending=asc).reset_index(drop=True).head(rcnt)

    dict = sdf.set_index('president')['count'].to_dict()
    print(dict)
    
    return dict

def print_group_by_count(keyword: str, asc: bool=False, rcnt: int=12):
    df = group_by_count(keyword, asc, rcnt)
    print(df.to_string(index=False))

def print_add_keyword_count(keyword: str, asc: bool=False, rcnt: int=12, keyword_sum:bool=True):
    df = add_keyword_count(keyword, asc, rcnt, keyword_sum)
    print(df.to_string(index=False))


def entry_point():
    typer.run(print_group_by_count)

def entry_point_cnt():
    typer.run(print_add_keyword_count)

def entry_point_dict():
    typer.run(group_by_count_to_dict)
