from glob import glob
import os
import gpxpy
import numpy as np


def load_all_gpx(folder: str, sample=0) -> list[gpxpy.gpx.GPXTrackPoint]:
    """Load all gpx files in folder.

    ## Parameters
    - folder (str) - where to look for files.
    - sample (int) - if positive, only load a random sample of files.

    ## Returns
    - activities (list) - ??
    """
    rng = np.random.default_rng()
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
