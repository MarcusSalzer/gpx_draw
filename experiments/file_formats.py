"""
## Comparison of file formats and libraries for storing and loading points data

- Dataframes contain numeric, string and datetime types
- Loading times include all parsing.

"""

from timeit import timeit, default_timer
import pandas as pd
import os
import polars as pl


MAX_FILES = 100
original_dir = "data/points_pandas"

timings = {}


print("loading original...")
tmp = default_timer()
all_acts: dict[str, pd.DataFrame] = {}
original_size = 0
for filename in os.listdir(original_dir)[:MAX_FILES]:
    fp = os.path.join(original_dir, filename)
    df = pd.read_json(fp, convert_dates=["time"])
    all_acts[filename.split(".")[0]] = df
    original_size += os.path.getsize(fp)

timings["pandas_json"] = {
    "load": default_timer() - tmp,
    "size": original_size / (1024 * 1024.0),
}

print(f"loaded original ({len(all_acts)} files)")
print(f"original filesize {original_size/(1024*1024.0):.1f} MB")

example = list(all_acts.values())[0]
# print(example.dtypes)
# print(example.head())


print("saving parquet...")
tmp = default_timer()
for k in all_acts.keys():
    path = "data/points_parquet/" + k + ".parquet"
    all_acts[k].to_parquet(path)

timings["pandas_parquet"] = {"save": default_timer() - tmp}

print("loading parquet...")

tmp = default_timer()
all_acts_pd_p = {}
pd_p_size = 0
for k in all_acts.keys():
    fp = "data/points_parquet/" + k + ".parquet"
    all_acts_pd_p[k] = pd.read_parquet(fp)
    pd_p_size += os.path.getsize(fp)

timings["pandas_parquet"]["load"] = default_timer() - tmp
timings["pandas_parquet"]["size"] = pd_p_size / (1024 * 1024.0)
example_pd_p = list(all_acts_pd_p.values())[0]


for k in all_acts.keys():
    assert all_acts[k].equals(all_acts_pd_p[k]), "Incorrect pandas_parquet"


print("\nTIMINGS")
print(pd.DataFrame.from_dict(timings, orient="index").to_markdown())
