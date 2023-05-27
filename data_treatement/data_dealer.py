from datetime import datetime, timedelta

def convert_to_timestamp(df, column:str):
    df[column] = df[column].apply(lambda x: datetime.fromisoformat(str(x)) + timedelta(hours=-3))


def clear_rows(df):
    df.dropna(axis=0, how='any', inplace=True)
    df.sort_values(by=['payloaddatetime', 'PLM'], ascending=[False, True], inplace=True)