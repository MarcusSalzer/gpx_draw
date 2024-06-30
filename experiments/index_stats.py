import os
from timeit import default_timer
from typing import Literal

import polars as pl

from app_functions import data_functions as dataf
from app_functions import plot_functions as plotf
from app_functions import stats_functions as statsf

ACT_DIR = "data/points_parquet"
INDEX_PATH = "data/activity_index.parquet"

tmp = default_timer()
act_index = dataf.load_parquet(INDEX_PATH)
t_load_index = default_timer() - tmp

# for now, only main sports
SPORTS = act_index["sport_main"].unique().to_list()

# interval for all summaries
INTERVAL: Literal["1d", "1w", "1mo", "1y"] = "1mo"


tmp = default_timer()
summary = statsf.summary_interval(act_index, INTERVAL)
t_sum_main = default_timer() - tmp

tmp = default_timer()
summaries = dict.fromkeys(SPORTS)
for sport in SPORTS:
    summaries[sport] = statsf.summary_interval(
        act_index.filter(pl.col("sport_main") == sport), INTERVAL
    )
t_sum_sports = default_timer() - tmp

if __name__ == "__main__":
    print("loaded index:", t_load_index)
    print("made day summary  :", t_sum_main)
    print("made sport summaries  :", t_sum_sports)

    # print(summary_month.head())
    # plot_summary_month()

    # print(act_index)
    # print(summary)

    plot_summaries = ["cycling", "running", "walking"]

    # summary_fig = plotf.plot_summary_histogram(summary[-12:], y="count")
    summary_fig = plotf.multi_summary_hist(
        [summaries[s] for s in plot_summaries],
        names=plot_summaries,
        y_col="count",
        plot_type="line",
    )
    summary_fig.show()

    print("unique sports:", SPORTS)
