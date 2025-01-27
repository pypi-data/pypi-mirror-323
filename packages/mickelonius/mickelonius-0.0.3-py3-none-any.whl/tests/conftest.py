import math
import pathlib
import pytest
import pandas as pd
import numpy as np
import itertools
import dask.dataframe as dd
from pyspark.sql import SparkSession

from tests.utils import get_daily_spy
from tests import test_data_path

test_k_pct = 0.01
test_f = 100.0


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .appName("pytest-pyspark") \
        .master("local[*]") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .getOrCreate()


@pytest.fixture
def nonstationary_series():
    np.random.seed(42)
    data = np.cumsum(np.random.randn(1000))  # Random walk
    yield pd.Series(data)


@pytest.fixture
def tick_df_pandas():
    test_df = pd.read_csv(f'{test_data_path}/IVE_tickbidask_subset.txt', header=None,
                          names=['Date', 'Time', 'Price', 'Bid', 'Ask', 'Size'])
    test_df['dt_str'] = test_df.Date.str.cat(test_df.Time, sep=" ")
    test_df['t'] = pd.to_datetime(test_df['dt_str'])
    test_df = test_df.drop(labels=['dt_str', 'Date', 'Time', ], axis=1)
    test_df.set_index('t', inplace=True)
    test_df.sort_index(inplace=True)

    yield test_df


@pytest.fixture
def daily_spy_data():
    df = get_daily_spy(test_data_path / 'SPY.csv')
    df["Date"] = pd.to_datetime(df["Date"])
    return df


@pytest.fixture
def daily_spy_data_dask(daily_spy_data):
    daily_spy_data['Year'] = daily_spy_data['Date'].dt.year  # Extract the year
    df_dask = dd.from_pandas(
        daily_spy_data,
        npartitions=len(daily_spy_data['Year'].unique())
    )
    df_dask = df_dask.set_index('Date')
    # df_dask = df_dask.map_partitions(
    #     lambda df: df.sort_index()
    # ).repartition(
    #     divisions=[
    #                   daily_spy_data[daily_spy_data['Year'] == year]['Date'].min()
    #                   for year in daily_spy_data['Year'].unique()
    #               ]  # + [daily_spy_data['Date'].max()]
    # )
    df_dask = df_dask.repartition(partition_size='64MB')
    df_dask = df_dask.drop(columns=['Year'])
    yield df_dask


@pytest.fixture
def simple_encode_test_df_pandas():
    yield pd.DataFrame.from_dict(generate_simple_encode_dict())


@pytest.fixture
def simple_encode_test_df_dask():
    yield dd.from_pandas(pd.DataFrame.from_dict(generate_simple_encode_dict()), npartitions=2)


def generate_multi_encode_dict():
    f1 = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A',
          'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B',
          'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', ]
    f2 = ['Y', 'X', 'X', 'Y', 'X', 'Z', 'X', 'Y',
          'X', 'X', 'X', 'X', 'Y', 'Z', 'X', 'Z', 'X', 'Y', 'Z',
          'X', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'X', ]
    o = [1, 0, 1, 1, 1, 1, 0, 0,
         0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0,
         0, 1, 1, 1, 1, 1, 0, 0, ]

    p = sum(o)/len(o)
    combos = [e for e in itertools.product(list(set(f1)), list(set(f2)))]
    counts = {k: 0 for k in combos}
    sums = {k: 0 for k in combos}
    f1f2 = list(zip(f1, f2, o))
    for f in f1f2:
        k = tuple(f[:2])
        counts[k] += 1
        sums[k] += f[2]
    loo = []
    ema_loo = []
    for f in f1f2:
        k = tuple(f[:2])
        if counts[k] > 1:
            loo_val = (sums[k] - f[2]) / (counts[k] - 1)
            loo.append(loo_val)
            l = 1 / (1 + math.exp(-(counts[k] - test_k_pct * len(o)) / test_f))
            ema_loo.append(l * loo_val + (1 - l) * p)
        elif counts[k] == 1:
            loo.append(sums[k])
            ema_loo.append(sums[k])
        else:
            loo.append(0.5)
            ema_loo.append(0.5)
    return {
        'Feature1': f1,
        'Feature2': f2,
        'Outcome': o,
        'LOOEncode': loo,
        'EMA_LOOEncode': ema_loo,
    }


def generate_simple_encode_dict():
    f1 = ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', ]
    #'NumericFeature1': [0.22, 0.35, 0.12, 0.24, 0.45, 0.14, 0.74, 0.39, 0.14, ],
    o = [1, 0, 1, 1, 1, 1, 0, 1, 1, ]
    # [2. / 3., 1.00, 2. / 3., 2. / 3., 0.50, 0.50, 1.00, 1.00, 1.00, ]

    p = sum(o)/len(o)
    combos = set(f1)
    counts = {k: 0 for k in combos}
    sums = {k: 0 for k in combos}
    f1o = list(zip(f1, o))
    for f in f1o:
        k = f[0]
        counts[k] += 1
        sums[k] += f[1]
    loo = []
    ema_loo = []
    for f in f1o:
        k = f[0]
        if counts[k] > 1:
            loo_val = (sums[k] - f[1]) / (counts[k] - 1)
            loo.append(loo_val)
            l = 1 / (1 + math.exp(-(counts[k] - test_k_pct * len(o)) / test_f))
            ema_loo.append(l * loo_val + (1 - l) * p)
        elif counts[k] == 1:
            loo.append(sums[k])
            ema_loo.append(sums[k])
        else:
            loo.append(0.5)
            ema_loo.append(0.5)
    return {
        'Feature1': f1,
        'Outcome': o,
        'LOOEncode': loo,
        'EMA_LOOEncode': ema_loo,
    }


@pytest.fixture
def multi_encode_test_df_pandas():
    yield pd.DataFrame.from_dict(generate_multi_encode_dict())


@pytest.fixture
def multi_encode_test_df_dask():
    yield dd.from_pandas(pd.DataFrame.from_dict(generate_multi_encode_dict()), npartitions=2)
