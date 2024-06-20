import os
from app_functions import data_functions as dataf
from app_functions import stats_functions as statsf
from app_functions import plot_functions as plotf

from timeit import default_timer

ACT_DIR = "data/points_parquet"
INDEX_PATH = "data/activity_index.parquet"

tmp = default_timer()
act_index = dataf.load_parquet(INDEX_PATH)
t_load_index = default_timer() - tmp

print(act_index.sort("start_time"))

tmp = default_timer()
summary_month = statsf.summary_month(act_index)
t_sum_month = default_timer() - tmp


def plot_summary_month():
    fig = plotf.plot_summary_month(summary_month, y="duration", last_year_only=False)
    fig.show()


if __name__ == "__main__":
    print("loaded index:", t_load_index)
    print("made month summary:", t_sum_month)

    # plot_summary_month()
