import os
from app_functions import data_functions as dataf
from app_functions import stats_functions as statsf
import polars as pl

ACT_DIR = "data/points_parquet"
INDEX_PATH = "data/activity_index.parquet"

files = dataf.find_importable(ACT_DIR, [".parquet"])

print(files)

print("loading files...", end=" ")

all_acts = dict.fromkeys(files["name"])
for name, path in zip(files["name"], files["path"]):
    all_acts[name] = dataf.load_parquet(path, {"time"})

print("Done!")

print("indexing...", end="")
act_index = dataf.index_activities_polars(all_acts)

lengths = []
for k in all_acts.keys():
    lengths.append(round(statsf.trace_distance(all_acts[k], "small-angle")[-1, "dist"]))

act_index = act_index.with_columns(
    pl.Series(name="length", values=lengths, dtype=pl.UInt32)
)

print(act_index)

dataf.safe_save(act_index, INDEX_PATH, overwrite=True, check_read=True)

print("Done!")
