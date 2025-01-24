from president_speech.db.parquet_interpreter import read_parquet, get_parquet_full_path
import pandas as pd
import typer
import time
from tqdm import tqdm

def psearch_by_count():
    data_path = get_parquet_full_path()
    df = pd.read_parquet(data_path)
    
    while True:
        keyword = input ("검색할 키워드를 입력하세요(종료를 원하면 '종료하겠습니다'를 입력하세요)")
        if keyword == '종료하겠습니다':
            print ("종료합니다")
            break
        f_df = df[df['speech_text'].str.contains(str(keyword), case=False)]
        if not f_df.empty:
            rdf = f_df.groupby("president").size().reset_index(name="count").sort_values(by="count", ascending=False)
            sdf = rdf.sort_values(by='count', ascending=False).reset_index(drop=True)
            print(sdf.to_string(index=False))
        
        else:
            print("일치하는 값이 없습니다")
            continue 

def group_by_count(keyword: str,asorde: bool,howmany: int):
    # TODO: ascending, 출력 rows size 이들의 변수 고려
    # pytest 코드 작성해보기
    # import this <- 해석해보세요
    data_path = get_parquet_full_path()
    df = pd.read_parquet(data_path)
    f_df = df[df['speech_text'].str.contains(keyword, case=False)]
    rdf = f_df.groupby("president").size().reset_index(name="count")
    sdf = rdf.sort_values(by='count', ascending=asorde).reset_index(drop=True)
    rdf = sdf.head(howmany)
    return rdf

def print_group_by_count(keyword: str,asorde: bool,howmany: int):
    rdf=group_by_count(keyword,asorde,howmany)
    for i in tqdm(range(len(rdf.columns)*len(rdf.index))):
        pass
    time.sleep(2)
    print(rdf.to_string(index=False))


def entry_point():
    typer.run(print_group_by_count)

def add_keyword_count(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """
    DataFrame에 keyword_count 컬럼을 추가하여 반환합니다.
    각 speech_text에서 keyword가 등장하는 횟수를 계산합니다.
    """
    # keyword_count 컬럼 추가
    df['keyword_count'] = df['speech_text'].str.count(keyword)
    return df

def group_by_count_akc(keyword: str, asorde: bool=False, howmany: int=12, keyword_sum: bool=False) -> pd.DataFrame:
    data_path = get_parquet_full_path()
    df = pd.read_parquet(data_path)
    fdf = df[df['speech_text'].str.contains(keyword, case=False)]
    
    if(keyword_sum):
        fdf = add_keyword_count(fdf.copy(), keyword)
        gdf = fdf.groupby("president").agg(
            count=("speech_text", "size"),  # 연설 개수
            keyword_sum=("keyword_count", "sum")  # keyword 발생 횟수 합산
        )
        sdf = gdf.sort_values(by=["keyword_sum", "count"], ascending=[asorde, asorde]).reset_index()
    else:
        gdf = fdf.groupby("president").size().reset_index(name="count")
        sdf = gdf.sort_values(by='count', ascending=asorde).reset_index(drop=True)
    
    rdf = sdf.head(howmany)
    return rdf

def print_group_by_count_akc(keyword: str, asorde: bool=False, howmany: int=12, keyword_sum: bool=False):
    df = group_by_count_akc(keyword, asorde, howmany, keyword_sum)
    #프로그레스바 추가 해보기 - df 컬럼 숫자 * row 숫자 + sleep
    for i in tqdm(range(len(df.columns)*len(df.index))):
        pass
    time.sleep(2) 
    print(df.to_string(index=False))


def entry_point_akc():
    typer.run(print_group_by_count_akc)
