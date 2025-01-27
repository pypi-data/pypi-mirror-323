import pandas as pd


def get_daily_spy(file_path):
    """
    # SPY.csv is a csv with header/columns
    # Date,Open,High,Low,Close,Volume,Adj Close,Side
    # where Side is -1 or 1 and used for meta-labelling
    :return:
    """
    test_df = pd.read_csv(file_path)
    test_df["t"] = pd.to_datetime(test_df.Date)
    test_df.set_index("t", inplace=True)
    test_df.sort_index(inplace=True)

    return test_df
