import os
from app_functions import data_functions as dataf
from app_functions import stats_functions as statsf
from app_functions import plot_functions as plotf

from timeit import default_timer

ACT_DIR = "data/points_parquet"
INDEX_PATH = "data/activity_index.parquet"

act_index = dataf.load_parquet(INDEX_PATH)

act_id = act_index.sort("start_time")[-1, "id"]

act = dataf.load_parquet(os.path.join(ACT_DIR, act_id + ".parquet"))
print(act)

tmp = default_timer()
dist = statsf.hav_distance(act)
t_havformula = default_timer() - tmp

print(dist)
print(f"total dist: {dist[-1,'dist_km']:.2f} km")
print("compute time:", t_havformula)
