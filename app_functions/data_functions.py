import fnmatch
import gzip
import json
import os
import shutil
from glob import glob

import fitdecode
import gpxpy
import gpxpy.gpx
import numpy as np
import pandas as pd
import msgspec.json

from app_functions.activity import Act

IMPORT_TYPES = [".gpx", ".gpx.gz", ".fit", ".fit.gz", ".json", ".json.gz"]


def unzip_gz(folder: str, file: str, overwrite=False):
    """Unzip a file and save a copy.
    ## Parameters
    - folder
    - file
    - overwrite (bool): If true, overwrite existing file with same name."""

    assert file[-3:] == ".gz", "want .gz filename"

    file_out = file[:-3]  # remove .gz extension
    if (file_out in os.listdir(folder)) and (not overwrite):
        return False

    with gzip.open(os.path.join(folder, file), "rb") as f_in:
        with open(os.path.join(folder, file_out), "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return True


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
        act_info = info_from_gpx_track(track)

        # add to index
        act_index["activities"][file] = act_info

        if verbose:
            print(act_info)

        print(f"indexed file {i+1}/{len(filenames)}.")

    # add metadata to index
    now = pd.Timestamp.now()
    act_index["created"] = now
    act_index["updated"] = now
    return act_index


def info_from_gpx_track(track) -> dict[str]:
    """Extract common metadata from a gpx_track"""
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
    return act_info


def check_index(act_index: dict):
    """Check index for duplicates and more"""

    info = []

    info.append("index created : %s" % act_index["created"])
    info.append("index updated : %s" % act_index["updated"])
    info.append("since update  : %s" % (pd.Timestamp.now() - act_index["updated"]))

    acts = act_index["activities"]
    duplicates = find_duplicates(acts)

    info.append("activity count: %s" % len(acts))
    info.append("found duplicates :%s" % len(duplicates))

    return info


def find_duplicates(acts: dict):
    matches = []
    act_list = list(acts.values())
    names_list = list(acts.keys())

    for i, a1 in enumerate(act_list[:-1]):
        for j in range(i + 1, len(act_list)):
            a2 = act_list[j]
            if a1 == a2:
                matches.append((i, j))
    return [(names_list[i], names_list[j]) for i, j in matches]


def serialize_json(obj):
    """Create resonable serializations for datatypes used here."""
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="dict")
    raise TypeError("cannot serialize object (%s)" % type(obj))


def load_act_index(filepath) -> dict:
    """Load activity index from JSON.

    ## Returns
    - act_index (dict): with keys 'activities', 'updated' and 'created'.
        - 'activities' is a list of dicts with keys 'name'...
    """
    with open(filepath, encoding="utf8") as f:
        act_index = json.load(f)

    # convert to datetime
    act_index["updated"] = pd.Timestamp(act_index["updated"])
    act_index["created"] = pd.Timestamp(act_index["created"])

    for k in act_index["activities"].keys():
        act_index["activities"][k]["time_start"] = pd.Timestamp(
            act_index["activities"][k]["time_start"]
        )
        act_index["activities"][k]["time_end"] = pd.Timestamp(
            act_index["activities"][k]["time_end"]
        )
    return act_index


def save_json(filepath, obj):
    """Save object as JSON.

    ## Parameters
    - filepath (str): destination file. Will be compressed if ends with '.gz'."""

    if filepath[-3:] == ".gz":
        json_bytes = json.dumps(obj, default=serialize_json).encode("utf-8")
        with gzip.open(filepath, mode="w") as f:
            f.write(json_bytes)
    else:
        with open(filepath, mode="w", encoding="utf8") as f:
            json.dump(obj, f, default=serialize_json, indent=0)

    return True


def load_json(filepath: str, enc="utf8") -> dict:
    """Load..."""
    # choose based on filetype
    if filepath[-3:] == ".gz":
        with gzip.open(filepath) as f:
            return json.load(f)
    else:
        with open(filepath, encoding=enc) as f:
            return json.load(f)


def save_settings(filepath: str, settings_dict: dict):
    with open(filepath, "w") as f:
        json.dump(settings_dict, f, indent=4)


def load_all_gpx(folder: str, sample=0) -> list[gpxpy.gpx.GPX]:
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


def load_fit(filepath: str):
    """Load a .fit-file, or compressed .fit.gz-file.

    Extract point-wise data from data-message named "record".

    ## Returns
    - act_dict (dict): dict of activity data (no processing or datatypes converted)
    """

    record_fields = {
        "timestamp": "time",
        "position_lat": "lat",
        "position_long": "long",
        "enhanced_speed": "speed_enh",
        "enhanced_altitude": "alt_enh",
        "heart_rate": "hr",
    }

    points = {k: [] for k in record_fields.values()}
    act_dict = {}

    # choose based on filetype
    if filepath[-3:] == ".gz":
        openfunc = gzip.open
    else:
        openfunc = open

    with openfunc(filepath, "rb") as f:
        with fitdecode.FitReader(f, check_crc=fitdecode.CrcCheck.RAISE) as fit:
            for frame in fit:
                # frame with data?
                if frame.frame_type == fitdecode.FIT_FRAME_DATA:
                    if frame.name == "record":
                        for k in record_fields.keys():
                            points[record_fields[k]].append(
                                frame.get_value(k, fallback=None)
                            )
                    elif frame.name == "sport":
                        sport_name = frame.get_value("name")
                        sport_main = frame.get_value("sport")
                        sport_sub = frame.get_value("sub_sport")
                        act_dict["sport"] = [sport_name, sport_main, sport_sub]
        act_dict["points"] = points

        return act_dict


def eddington_nbr(act_index: dict) -> int:
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


def find_importable(folder: str, extensions=IMPORT_TYPES):
    """Find all files that could be imported as activities."""

    matches = []
    for root, dirnames, filenames in os.walk(folder):
        for extension in extensions:
            for filename in fnmatch.filter(filenames, f"*{extension}"):
                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                matches.append((file_path, file_size, extension))
    return pd.DataFrame(sorted(matches), columns=["path", "size", "type"])


def convert_activity_json(
    filepath: str,
    folder_out: str,
    overwrite=False,
    compress=False,
):
    """Load activity file and save as JSON.

    ## Parameters
    - filepath (str): path to file (.fit, .fit.gz) #TODO GPX?
    - output_folder (str): destination folder
    - overwrite (bool): If true, convert and overwrite existing files
    - compress (bool): If true, save as a compressed .json.gz file
    - verbose (bool)

    ## Returns
    - completed (bool): transaction completed
    """

    name, extension = os.path.split(filepath)[-1].split(".", maxsplit=1)

    if compress:
        extension_out = ".json.gz"
    else:
        extension_out = ".json"

    path_out = os.path.join(folder_out, name + extension_out)

    # Check if already exists
    if (not overwrite) and os.path.exists(path_out):
        return False

    act = Act.from_dict(load_fit(filepath))
    save_json(filepath=path_out, obj=act.to_dict())
    return True


# TODO: include indexing here?
def convert_all_activities_json(
    folder_in: str, folder_out: str, overwrite=False, compress=False, verbose=False
):
    """Convert all activities in the folder to json"""

    files = find_importable(folder_in, extensions=[".fit", ".fit.gz"])["path"]

    if verbose:
        print("found files", len(files))

    for i, file in enumerate(files):
        converted = convert_activity_json(file, folder_out, overwrite, compress)
        if verbose:
            if converted:
                print(i, "Convert", file)
            else:
                print(i, "Skip   ", file)
