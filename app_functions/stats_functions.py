from math import pi
from typing import Literal

import numpy as np
import polars as pl


def summary_interval(
    act_index: pl.DataFrame,
    interval: Literal["1d", "1w", "1mo", "1y"],
):
    """Summarize activity index over a desired interval

    ## Returns
    - summary (pl.Dataframe): summary from first to last activity, with one row per `interval`.
        - date
        - duration
        - length
        - count
        - label
    """

    if interval not in ("1d", "1w", "1mo", "1y"):
        raise ValueError("Unsupported interval")

    # sort to before group dynamic
    act_index = act_index.sort("start_time")

    summary = (
        act_index.group_by_dynamic(index_column="start_time", every=interval)
        .agg(
            pl.col("duration").sum(),
            pl.col("length").sum(),
            count=pl.len(),
        )
        .with_columns(date=pl.col("start_time").cast(pl.Date))
        .drop("start_time")
        .upsample(time_column="date", every=interval, maintain_order=True)
        .fill_null(0)
    )

    if interval == "1y":
        summary = summary.with_columns(label=pl.col("date").dt.strftime("%Y"))
    if interval == "1mo":
        summary = summary.with_columns(label=pl.col("date").dt.strftime("%b %Y"))
    if interval == "1w":
        summary = summary.with_columns(label=pl.col("date").dt.strftime("w%W %Y"))
    return summary


def summary_month(act_index: pl.DataFrame):
    """Summarize activity index over months"""
    summary = (
        act_index.group_by(
            pl.col("start_time").dt.year().alias("year"),
            pl.col("start_time").dt.month().alias("month"),
        )
        .agg(pl.col("duration").sum(), pl.col("length").sum(), pl.len().alias("count"))
        .sort("year", "month")
    ).with_columns(
        [
            (
                pl.col("year").cast(pl.Utf8)
                + "-"
                + ("0" + pl.col("month").cast(pl.Utf8)).str.slice(-2)
            ).alias("month_label"),
            (12 * pl.col("year") + pl.col("month")).alias("month_nbr"),
        ]
    )

    return summary


def eddington_nbr(daily_summary):
    pass


def eddington_nbr_old(act_index: dict) -> int:
    """Compute all time Eddington number (km/day) for all activities.
    Based on 2d-distance per day"""

    # count distance per day
    dist_per_day = {}
    for k in act_index["activities"].keys():
        date = str(act_index["activities"][k]["time_start"].date())
        if date in dist_per_day.keys():
            dist_per_day[date] += act_index["activities"][k]["length2d_m"]
        else:
            dist_per_day[date] = act_index["activities"][k]["length2d_m"]

    # Covert m -> km, sort descending.
    dists = sorted((np.array(list(dist_per_day.values())) / 1000), reverse=True)

    # Compute E. i counts number of days, d is the distance
    E = 0
    for i, d in enumerate(dists):
        if d >= i + 1:
            E = i + 1
    return E


def trace_distance(
    points: pl.DataFrame,
    method: Literal["haversine", "small-angle"] = "haversine",
):
    """Compute distance between succesive points (haversine formula)

    ## Parameters
    - points (pl.DataFrame): containing integer lat/long
    - TODO 3D distance ?

    ## Returns
    - result (pl.DataFrame)
        - cumulative distance (km)
        - pointwise speed (km/h, m/s)

    """

    if not {"lat", "long"}.issubset(points.columns):
        raise ValueError("missing columns 'lat' or 'long'.")

    factor = 2**32 / 360  # convert to degrees
    R = 6371000  # approx earth radius

    coords_rad: pl.DataFrame = (
        points.select(pl.col("lat").alias("lat2"), pl.col("long").alias("lon2"))
        / factor
        * pi
        / 180
    )

    # shifted coordinates makes pairs
    coords_rad = coords_rad.with_columns(
        pl.col("lat2").shift(1).alias("lat1"),
        pl.col("lon2").shift(1).alias("lon1"),
    )

    if method == "haversine":

        def d_pair(lat1, lon1, lat2, lon2) -> pl.Expr:
            return (
                2
                * R
                * (
                    (lat2 - lat1).truediv(2).sin().pow(2)
                    + (lat1.cos() * lat2.cos()) * (lon2 - lon1).truediv(2).sin().pow(2)
                )
                .sqrt()
                .arcsin()
            )
    elif method == "small-angle":

        def d_pair(lat1, lon1, lat2, lon2) -> pl.Expr:
            return (
                R
                * (
                    ((lon2 - lon1) * (lat1 + lat2).truediv(2).cos()).pow(2)
                    + (lat2 - lat1).pow(2)
                ).sqrt()
            )

    else:
        raise ValueError("unknown method")

    result = pl.concat(
        [
            coords_rad.with_columns(
                dist=d_pair(
                    pl.col("lat1"), pl.col("lon1"), pl.col("lat2"), pl.col("lon2")
                ),
            ),
            points.select(
                pl.col("time").diff().dt.total_milliseconds() / (1000 * 3600)
            ),
        ],
        how="horizontal",
    )
    return (
        result.select(
            pl.col("dist"), (pl.col("dist") / (pl.col("time"))).alias("speed_kmh")
        )
        .with_columns(
            pl.col("dist").cum_sum(), (pl.col("speed_kmh") / 3.6).alias("speed_ms")
        )
        .fill_null(0)
    )
