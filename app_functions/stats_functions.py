import numpy as np
import polars as pl


def summary_month(act_index: pl.DataFrame):
    summary_month = (
        act_index.group_by(
            pl.col("start_time").dt.year().alias("year"),
            pl.col("start_time").dt.month().alias("month"),
        )
        .agg(pl.col("duration").sum(), pl.len().alias("count"))
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

    return summary_month


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


def hav_distance(points: pl.DataFrame):
    """Compute distance between succesive points (haversine formula)
    
    ## Parameters
    - points (pl.DataFrame): containing integer lat/long

    ## Returns
    - result (pl.DataFrame)
        - cumulative distance (km)
        - pointwise speed (km/h, m/s)
    
    """

    if not {"lat", "long"}.issubset(points.columns):
        raise ValueError("missing columns 'lat' or 'long'.")

    factor = 2**32 / 360  # convert to degrees
    R = 6373.0  # approx earth radius

    coords_rad: pl.DataFrame = (
        points.select(pl.col("lat").alias("lat2"), pl.col("long").alias("lon2"))
        / factor
        * np.pi
        / 180
    )

    # shifted coordinates makes pairs
    coords_rad = coords_rad.with_columns(
        pl.col("lat2").shift(1).alias("lat1"),
        pl.col("lon2").shift(1).alias("lon1"),
    )

    def d_pair_pl(lat1: str, lon1: str, lat2: str, lon2: str) -> pl.Expr:
        lat1 = pl.col(lat1)
        lon1 = pl.col(lon1)
        lat2 = pl.col(lat2)
        lon2 = pl.col(lon2)

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

    result = pl.concat(
        [
            coords_rad.with_columns(
                d_pair_pl("lat1", "lon1", "lat2", "lon2").alias("dist_km"),
            ),
            points.select(
                pl.col("time").diff().dt.total_milliseconds() / (1000 * 3600)
            ),
        ],
        how="horizontal",
    )
    return (
        result.select(
            pl.col("dist_km"), (pl.col("dist_km") / (pl.col("time"))).alias("speed_kmh")
        )
        .with_columns(
            pl.col("dist_km").cum_sum(), (pl.col("speed_kmh") / 3.6).alias("speed_ms")
        )
        .fill_null(0)
    )
