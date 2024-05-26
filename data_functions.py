from glob import glob
import os
from datetime import datetime, date
import gpxpy
import gpxpy.gpx
import numpy as np
from plotly import express as px, graph_objects as go, subplots as ps
import pandas as pd
import json

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def index_activities(folder: str, old_index=None, verbose=False) -> dict[str]:
    """Create or update(TODO) a index of all gpx-files in activities folder.

    The index is a dict indexed by ``id``, containing dicts with basic information.

    ## Parameters
    - folder (str): location to search for gpx-files.
    - old_index (TODO)

    ## Returns
    - index (dict)
    """
    filenames = glob("*.gpx", root_dir=folder)

    act_index = dict()
    act_index["activities"] = dict()

    for i, file in enumerate(filenames):
        # load a gpx
        with open(os.path.join(folder, file), encoding="utf8") as f:
            gpx: gpxpy.gpx.GPX = gpxpy.parse(f, "lxml")

        # check file assumptions
        if len(gpx.tracks) > 1:
            print(f"Multiple tracks not supported, excluding {file}")
            continue
        if not (gpx.tracks):
            print(f"No tracks, excluding {file}")
            continue
        if len(gpx.tracks[0].segments) > 1:
            print(f"Multiple segments not supported, excluding {file}")
            continue
        if not (gpx.tracks[0].segments):
            print(f"No segments, excluding {file}")
            continue

        track = gpx.tracks[0]
        # extract metadata
        act_info = dict()
        act_info["name"] = track.name
        act_info["desc"] = track.description
        act_info["comment"] = track.comment
        act_info["type"] = track.type
        act_info["source"] = track.source
        act_info["n_points"] = len(track.segments[0].points)
        act_info["length2d_m"] = track.length_2d()  # lat,long-length [m]
        act_info["length3d_m"] = track.length_3d()  # lat,long,elev-length [m]

        act_info["time_start"] = track.get_time_bounds().start_time
        act_info["time_end"] = track.get_time_bounds().end_time

        # add to index
        act_index["activities"][file] = act_info

        if verbose:
            print(act_info)

        print(f"indexed file {i+1}/{len(filenames)}.")

    # add metadata to index
    now = datetime.now()
    act_index["created"] = now
    act_index["updated"] = now
    return act_index


def serialize_json(obj):
    """Create resonable serializations for datatypes used here."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("cannot serialize object (%s)" % type(obj))


def load_act_index(filepath):
    """Load activity index

    ## Returns
    - act_index (dict): with keys 'activities', 'updated' and 'created'.
        - 'activities' is a list of dicts with keys 'name'...
    """
    with open(filepath, encoding="utf8") as f:
        act_index = json.load(f)

    # convert to datetime
    act_index["updated"] = datetime.fromisoformat(act_index["updated"])
    act_index["created"] = datetime.fromisoformat(act_index["created"])

    for k in act_index["activities"].keys():
        act_index["activities"][k]["time_start"] = datetime.fromisoformat(
            act_index["activities"][k]["time_start"]
        )
        act_index["activities"][k]["time_end"] = datetime.fromisoformat(
            act_index["activities"][k]["time_end"]
        )
    return act_index


def save_act_index(filepath, act_index):
    """Save activity index"""
    with open(filepath, mode="w", encoding="utf8") as f:
        json.dump(act_index, f, default=serialize_json)


def load_all_gpx(folder: str, sample=0) -> list:
    """Load all gpx files in folder, using ``gpxpy``.

    ## Parameters
    - folder (str) - where to look for files.
    - sample (int) - if positive, only load a random sample of files.

    ## Returns
    - activities (list) - list of gpxpy.gpx.GPX objects.
    """
    activities = []
    filenames = glob("*.gpx", root_dir=folder)

    if sample > 0:
        filenames = np.random.choice(filenames, sample)

    for i, file in enumerate(filenames):
        with open(os.path.join(folder, file), "r", encoding="utf8") as f:
            gpx = gpxpy.parse(f, "lxml")
        if gpx.tracks and gpx.tracks[0].segments and gpx.tracks[0].segments[0].points:
            # add if not empty
            activities.append(gpx)

    return activities


def load_one_gpx(filepath: str):
    with open(filepath, "r", encoding="utf8") as f:
        gpx = gpxpy.parse(f, "lxml")
    if gpx.tracks and gpx.tracks[0].segments and gpx.tracks[0].segments[0].points:
        return gpx


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
    fig.add_trace(go.Scatter(x=time, y=elev), row=2, col=1)
    fig.update_layout(
        template="plotly_dark",
        title=act_name + " (%.2f km)" % length_km,
        showlegend=False,
        dragmode="pan",
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1, row=1, col=1)

    fig.update_xaxes(showgrid=show_grid)
    fig.update_yaxes(showgrid=show_grid)

    return fig


def summary_plot(act_index: dict):
    """Plot an overview of indexed activities."""

    df = pd.DataFrame.from_dict(act_index["activities"], orient="index")
    df["time_start"] = pd.to_datetime(df["time_start"], format="%Y-%m-%d %H:%M:%S")
    df["year"] = df["time_start"].dt.year
    act_year = df.groupby("year").size()

    fig = px.bar(act_year, template="plotly_dark")
    return fig
