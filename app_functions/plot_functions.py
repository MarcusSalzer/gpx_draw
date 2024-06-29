import gpxpy
import gpxpy.gpx
from plotly import express as px, graph_objects as go, subplots as ps, io as pio
import pandas as pd
import polars as pl
from datetime import datetime
from typing import Literal

PLOT_TEMPLATE = pio.templates["plotly_dark"]
PLOT_TEMPLATE.layout.autosize = False
PLOT_TEMPLATE.layout.width = 500
PLOT_TEMPLATE.layout.height = 300
PLOT_TEMPLATE.layout.margin = dict(t=50, l=80, r=50, b=50)
PLOT_TEMPLATE.layout.title.x = 0.5
PLOT_TEMPLATE.layout.dragmode = "pan"

pio.templates.default = PLOT_TEMPLATE


def plot_one_gpx(gpx: gpxpy.gpx.GPX = None, show_grid=False) -> go.Figure:
    """Create a figure for one gpx.
    Note: supports only single track, single segment, gpx files"""

    if not gpx:
        return go.Figure()

    points = gpx.tracks[0].segments[0].points
    lat = [p.latitude for p in points]
    lon = [p.longitude for p in points]
    elev = [p.elevation for p in points]
    time = [p.time for p in points]
    act_name = gpx.tracks[0].name if gpx.name else "Activity"
    length_km = gpx.tracks[0].length_2d() / 1000

    fig = ps.make_subplots(
        rows=2, cols=1, row_heights=[0.7, 0.3], subplot_titles=["Trace", "Altitude"]
    )
    fig.add_trace(go.Scatter(x=lon, y=lat), row=1, col=1)
    fig.add_trace(go.Scatter(x=time, y=elev, fill="tozeroy"), row=2, col=1)
    fig.update_layout(
        title=act_name + " (%.2f km)" % length_km,
        showlegend=False,
        dragmode="pan",
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1, row=1, col=1)

    fig.update_xaxes(showgrid=show_grid)
    fig.update_yaxes(showgrid=show_grid)

    # freeze vertical in altitude plot
    fig.update_yaxes(fixedrange=True, row=2, col=1)

    return fig


def polar_summary_month(summary_month):
    data = (
        summary_month.group_by("month")
        .agg(pl.col("duration").sum(), pl.col("count").sum())
        .sort("month")
    )
    fig = go.Figure()
    fig.add_trace(
        go.Barpolar(
            r=data["count"],
            theta=data["month"].cast(str),
            marker_color=data["month"],
        )
    )
    fig.update_polars()
    fig.update_traces()
    fig.update_layout(title="monthly distribution")
    return fig


def plot_summary_year(summary_year):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=summary_year["year"],
            y=summary_year["count"],
            marker_color=summary_year["count"],
            orientation="v",
        )
    )
    fig.update_layout(title="activities per year")
    fig.update_xaxes(dtick=1)
    return fig


def plot_summary_month(summary_month: pl.DataFrame, y="count", last_year_only=True):
    if y not in ("count", "duration"):
        return NotImplemented

    dat = summary_month
    if last_year_only:
        now = datetime.now()
        month_nbr_now = now.year * 12 + now.month
        dat = dat.filter(pl.col("month_nbr") >= month_nbr_now - 12)

    if y == "count":
        name = "Activities"
        y_data = dat["count"]
    elif y == "duration":
        name = "Activity time"
        y_data = (dat["duration"].dt.total_minutes() / 60).round(1)

    fig = px.bar(
        dat,
        x="month_nbr",
        y=y_data,
        orientation="v",
        title=name + " per month" + " (last year)" * last_year_only,
    )

    if len(dat) < 14:
        xaxis = dict(
            tickmode="array",
            tickvals=dat["month_nbr"],
            ticktext=dat["month_label"],
        )
    else:
        xaxis = dict(
            tickmode="array",
            tickvals=dat["year"] * 12 + 6,  # OFFSET?
            ticktext=dat["year"],
        )
    fig.update_layout(
        xaxis=xaxis,
        xaxis_title=None,
        yaxis_fixedrange=True,
    )
    return fig


def multi_summary_hist(summaries, names=None):
    """Plot a list of summaries"""
    fig = go.Figure()
    for summ in summaries:
        fig.add_trace(
            go.Bar(
                x=summ["date"],
                y=summ["count"],
            )
        )
    return fig


def summary_hist(
    summary: pl.DataFrame,
    y: Literal["count", "length"] = "count",
):
    """Plot a histogram of a time-interval summary."""

    fig = px.bar(
        summary,
        x="date",
        y=y,
        orientation="v",
        title="Summary",
    )

    xaxis = dict(
        tickmode="array",
        tickvals=summary["date"],
        ticktext=summary["label"],
    )

    fig.update_layout(
        xaxis=xaxis,
        yaxis_fixedrange=True,
    )
    return fig


def plot_points_geo(lat, long):
    """TODO"""

    fig = go.Figure()

    factor = 2**32 / 360

    hov_tmp = "<br>".join(
        [
            "time: %{customdata[0]}",
        ]
    )
    fig = px.scatter_geo(
        lat=lat / factor,
        lon=long / factor,
        width=800,
        height=480,
        fitbounds="locations",
        title="Activity locations",
    )
    fig.update_layout(margin=dict(l=0, r=0, b=0))
    return fig


def points_map(data: pl.DataFrame):
    """Plot points on a open-street-map"""
    FACTOR_DEG = 2**32 / 360
    MAP_MARGIN = 0.05

    fig = px.scatter_mapbox(
        lat=data["lat"] / FACTOR_DEG,
        lon=data["long"] / FACTOR_DEG,
        hover_name=data["time"],
        hover_data=data["alt_enh", "hr"],
        color_discrete_sequence=["red"],
        # color=act["hr"].cast(pl.Float32),
        # color_continuous_scale="magma",
        height=600,
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(
        mapbox_bounds={
            "west": data["long"].min() / FACTOR_DEG - MAP_MARGIN,
            "east": data["long"].max() / FACTOR_DEG + MAP_MARGIN,
            "south": data["lat"].min() / FACTOR_DEG - MAP_MARGIN,
            "north": data["lat"].max() / FACTOR_DEG + MAP_MARGIN,
        }
    )
    return fig
