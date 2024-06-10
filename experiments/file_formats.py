"""
## Comparison of file formats and libraries for storing and loading points data

- Dataframes contain numeric, string and datetime types
- Loading times include all parsing.

"""

import pandas as pd
import os
import polars as pl
from utility import time_functions

MAX_FILES = 10
original_dir = "data/points_pandas"

timings = {}




def load_json_pd():
    all_acts: dict[str, pd.DataFrame] = {}
    size = 0
    for filename in os.listdir(original_dir)[:MAX_FILES]:
        fp = os.path.join(original_dir, filename)
        df = pd.read_json(fp, convert_dates=["time"])
        all_acts[filename.split(".")[0]] = df
        size += os.path.getsize(fp)
    return all_acts, size


all_acts, original_size = load_json_pd()

ACTS = all_acts.keys()

print(f"loaded original ({len(all_acts)} files)")
print(f"original filesize {original_size/(1024*1024.0):.1f} MB")

example = list(all_acts.values())[0]
# print(example.dtypes)
# print(example.head())


def save_parq_pd():
    for k in ACTS:
        path = "data/points_parquet/" + k + ".parquet"
        all_acts[k].to_parquet(path)


def load_parq_pd():
    all_acts = {}
    size = 0
    for k in ACTS:
        fp = "data/points_parquet/" + k + ".parquet"
        all_acts[k] = pd.read_parquet(fp)
        size += os.path.getsize(fp)
    return all_acts, size


funs = [
    load_json_pd,
    save_parq_pd,
    load_parq_pd,
]


timings, outputs = time_functions(
    funs,
    table_outputs={"size (MB)": 1},
    out_format=lambda x: f"{x/(1024.0**2):.2f}",
    verbose=True,
)
print(timings.to_markdown())


for k in ACTS:
    assert all_acts[k].equals(outputs["load_parq_pd"][0][k]), "Incorrect pandas_parquet"
