import gpxpy
import gpxpy.gpx
from plotly import express as px, graph_objects as go, subplots as ps
import pandas as pd


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


def summary_plot(act_index: dict):
    """Plot an overview of indexed activities."""

    df = pd.DataFrame.from_dict(act_index["activities"], orient="index")
    df["time_start"] = pd.to_datetime(df["time_start"], format="%Y-%m-%d %H:%M:%S")
    df["year"] = df["time_start"].dt.year
    act_year = df.groupby("year").size()

    fig = px.bar(act_year, template="plotly_dark")
    return fig
