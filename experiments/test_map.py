"""
Load an activity and plot on a map.
"""

import os
from timeit import default_timer

from app_functions import data_functions as dataf
from app_functions import plot_functions as plotf

ACT_DIR = "data/points_parquet"
INDEX_PATH = "data/activity_index.parquet"

tmp = default_timer()
act_index = dataf.load_parquet(INDEX_PATH)
t_load = default_timer() - tmp

act_id = act_index.sort("start_time")[-1, "id"]

act = dataf.load_parquet(os.path.join(ACT_DIR, act_id + ".parquet"))

tmp = default_timer()
fig = plotf.points_map(act)
fig.show()
t_plot = default_timer() - tmp

print(f"load time: {1000*t_load:.5g} ms")
print(f"plot time: {1000*t_plot:.5g} ms")
