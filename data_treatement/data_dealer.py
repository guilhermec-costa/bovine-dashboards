from datetime import datetime

def convert_to_timestamp(df, column:str):
    df[column] = df[column].apply(lambda x: datetime.fromisoformat(str(x)))


def clear_rows(df):
    df.dropna(axis=0, how='any', inplace=True)