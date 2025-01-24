from president_speech.db.parquet_interpreter import get_parquet_full_path
import pandas as pd
import typer

def group_by_count(keyword: str, asc: bool=False, rcnt: int=12)-> pd.DataFrame:
    data_path = get_parquet_full_path()
    df = pd.read_parquet(data_path)
    f_df = df[df['speech_text'].str.contains(keyword, case=False)]
    f_df.loc[:, 'kc'] = f_df['speech_text'].str.count(keyword)
    #gdf=f_df.groupby("president").size().reset_index(name="count")
    rdf = f_df.groupby("president", as_index=False).agg(count=('speech_text', 'size'), keyword_count=('kc', 'sum'))
    #sdf = gdf.sort_values(by='count', ascending=ascend).reset_index(drop=True)
    sdf = rdf.sort_values(by=['keyword_count', 'count'], ascending=[asc, asc]).reset_index(drop=True)
    if(rcnt <= 0):
        sdf = sdf
    elif(rcnt > len(sdf)):
        sdf = sdf
    else:
        sdf = sdf.head(rcnt)
    return sdf



def print_group_by_count(keyword: str, asc: bool=False, rcnt: int=12):
    df = group_by_count(keyword, asc, rcnt)
    print(df.to_string(index=False))

def entry_point():
    typer.run(print_group_by_count)

