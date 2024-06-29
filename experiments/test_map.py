import os

import plotly.express as px
import polars as pl

from app_functions import data_functions as dataf
from app_functions import plot_functions as plotf
from app_functions import stats_functions as statsf

ACT_DIR = "data/points_parquet"
INDEX_PATH = "data/activity_index.parquet"

act_index = dataf.load_parquet(INDEX_PATH)

act_id = act_index.sort("start_time")[-1, "id"]

act = dataf.load_parquet(os.path.join(ACT_DIR, act_id + ".parquet"))
print(act)

fig = plotf.points_map(act)
fig.show()
