def clear_rows(df, drop_mode, drop_axis, sort_by_cols, sort_sequence):
    df.dropna(axis=drop_axis, how=drop_mode, inplace=True)
    df.sort_values(by=sort_by_cols, ascending=sort_sequence, inplace=True)