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
            (pl.col("year").cast(pl.Utf8) + "-" + pl.col("month").cast(pl.Utf8)).alias(
                "month_label"
            ),
            (12 * pl.col("year") + pl.col("month")).alias("month_nbr"),
        ]
    )

    return summary_month
