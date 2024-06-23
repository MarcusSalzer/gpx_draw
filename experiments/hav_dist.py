import os
from app_functions import data_functions as dataf
from app_functions import stats_functions as statsf
from app_functions import plot_functions as plotf
import polars as pl

from timeit import default_timer, timeit


ACT_DIR = "data/points_parquet"
INDEX_PATH = "data/activity_index.parquet"

act_index = dataf.load_parquet(INDEX_PATH)

act_id = act_index.sort("start_time")[-1, "id"]

act = dataf.load_parquet(os.path.join(ACT_DIR, act_id + ".parquet"))
print(act)


print(act_index.head())


def compute_all_lengths(act_index: pl.DataFrame):
    lengths = []

    for act in act_index.iter_rows(named=True):
        try:
            act = dataf.load_parquet(
                os.path.join(ACT_DIR, act["id"] + ".parquet"),
                cols_required={"lat", "long"},
            )
        except ValueError:
            lengths.append(None)
            continue

        dist = statsf.trace_distance(act)
        lengths.append(dist[-1, "dist_km"])

    return pl.concat(
        [
            act_index.select("id"),
            pl.DataFrame(lengths, schema={"length": pl.Float32}),
        ],
        how="horizontal",
    )


N_TIMEIT = 1


if __name__ == "__main__":
    # lengths = compute_all_lengths(act_index)
    # act_index = act_index.drop("length").join(lengths, on="id")
    # print(act_index.sort("start_time").tail())

    # dataf.safe_save(act_index, INDEX_PATH)

    dist_hav = statsf.trace_distance(act, "haversine")

    dist_sa = statsf.trace_distance(act, "small-angle")

    print(f"haversine  dist : {dist_hav[-1,'dist']:.7f} m")
    print(f"small-angle dist: {dist_sa[-1,'dist']:.7f} m")
    print(
        "compute time haversine  :",
        timeit(lambda: statsf.trace_distance(act, "haversine"), number=N_TIMEIT)
        / N_TIMEIT,
    )
    print(
        "compute time small-angle:",
        timeit(lambda: statsf.trace_distance(act, "small-angle"), number=N_TIMEIT)
        / N_TIMEIT,
    )
