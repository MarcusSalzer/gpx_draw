import os
from app_functions import data_functions as dataf
from app_functions import stats_functions as statsf

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
dataf.safe_save(act_index, INDEX_PATH, overwrite=True, check_read=True)

print("Done!")
