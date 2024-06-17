import polars as pl


def summary_month(act_index: pl.DataFrame):
    summary_month = (
        act_index.sort("start_time")
        .group_by_dynamic("start_time", every="1m")
        .agg(pl.col("duration").sum(), pl.len().alias("count"))
        .with_columns(
            pl.col("start_time").dt.year().alias("year"),
            pl.col("start_time").dt.month().alias("month"),
        )
    )
    return summary_month