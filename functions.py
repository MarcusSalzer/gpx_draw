from glob import glob
import os
import gpxpy
import numpy as np
from plotly import express as px, graph_objects as go, subplots as ps


def load_all_gpx(folder: str, sample=0) -> list:
    """Load all gpx files in folder, using ``gpxpy``.

    ## Parameters
    - folder (str) - where to look for files.
    - sample (int) - if positive, only load a random sample of files.

    ## Returns
    - activities (list) - list of gpxpy.gpx.GPX objects.
    """
    activities = []
    found = glob("*.gpx", root_dir=folder)

    if sample > 0:
        found = np.random.choice(found, sample)

    for i, filename in enumerate(found):
        with open(os.path.join(folder, filename), "r", encoding="utf8") as f:
            gpx = gpxpy.parse(f, "lxml")
        if gpx.tracks and gpx.tracks[0].segments and gpx.tracks[0].segments[0].points:
            # add if not empty
            activities.append(gpx)

    return activities


def plot_one_gpx(gpx: gpxpy.gpx.GPX) -> go.Figure:
    """Create a figure for one gpx.
    Note: supports only single track gpx files"""
    points = gpx.tracks[0].segments[0].points
    lat = [p.latitude for p in points]
    lon = [p.longitude for p in points]
    elev = [p.elevation for p in points]
    time = [p.time for p in points]
    act_name = gpx.name if gpx.name else "Activity"
    length_km = gpx.tracks[0].length_2d() / 1000

    fig = ps.make_subplots(
        rows=2, cols=1, row_heights=[0.7, 0.3], subplot_titles=["Trace", "Altitude"]
    )
    fig.add_trace(go.Scatter(x=lon, y=lat), row=1, col=1)
    fig.add_trace(go.Scatter(x=time, y=elev), row=2, col=1)
    fig.update_layout(
        template="plotly_dark",
        title=act_name + " (%.2f km)" % length_km,
        showlegend=False,
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1, row=1, col=1)

    return fig
