import os
from app_functions import data_functions as dataf
from app_functions import stats_functions as statsf
import polars as pl

DATA_DIR = "data/points_parquet"
INDEX_PATH = "data/activity_index.parquet"

act_index = dataf.load_parquet(INDEX_PATH)

print("act index: ", len(act_index))
print(act_index.columns)

files = dataf.find_importable(DATA_DIR, [".json"])
print("metadata files: ", len(files))

rows = []

for fp in files["path"]:
    rows.append(pl.read_json(fp))

metadata = pl.concat(rows, how="diagonal_relaxed")

act_index = act_index.join(metadata, on="id")

print(act_index)

print(dataf.safe_save(act_index, INDEX_PATH, check_read=True))
