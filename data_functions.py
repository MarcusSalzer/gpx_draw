from glob import glob
import os
import gpxpy
import numpy as np
from plotly import express as px, graph_objects as go, subplots as ps


def index_activities(folder: str, old_index, verbose=False) -> dict[str, dict[str]]:
    """Create or update(TODO) a index of all gpx-files in activities folder.

    The index is a dict indexed by ``id``, containing dicts with basic information.

    ## Parameters
    - folder (str): location to search for gpx-files.
    - old_index (TODO)

    ## Returns
    - index (dict[str,dict])
    """
    filenames = glob("*.gpx", root_dir=folder)

    act_index = dict()

    for i, file in enumerate(filenames):
        # load a gpx
        with open(os.path.join(folder, file)) as f:
            gpx = gpxpy.parse(f, "lxml")

        # check file assumptions
        if len(gpx.tracks) > 1:
            print(f"Multiple tracks not supported,excluding {file}")
            continue
        if len(gpx.tracks[0].segments) > 1:
            print(f"Multiple segments not supported,excluding {file}")
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

        # add to index
        act_index[file] = act_info

        if verbose:
            print(act_info)

        print(f"indexed file {i+1}/{len(filenames)}.")
    return act_index


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


def plot_one_gpx(gpx: gpxpy.gpx.GPX, show_grid=False) -> go.Figure:
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

    fig.update_xaxes(showgrid=show_grid)
    fig.update_yaxes(showgrid=show_grid)

    return fig
