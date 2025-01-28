import wizata_dsapi


def sum_cols(context: wizata_dsapi.Context):
    df = context.dataframe.copy()
    df["sum_col"] = df.sum(axis=1)
    return df
