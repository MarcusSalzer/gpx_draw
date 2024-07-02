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
import polars as pl


# CONSTANTS

IMPORT_TYPES = [".gpx", ".gpx.gz", ".fit", ".fit.gz", ".json", ".json.gz"]
DEF_PL_PARQ_SCH = {
    "time": pl.Datetime(time_unit="us", time_zone="UTC"),
    "lat": pl.Null,
    "long": pl.Null,
    "speed_enh": pl.Null,
    "alt_enh": pl.Null,
    "hr": pl.UInt16,
}


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


def index_activities_gpx(folder: str, old_index=None, verbose=False) -> dict[str]:
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


def index_activities_polars(acts: dict[str, pl.DataFrame]) -> pl.DataFrame:
    """Index a dict of id:dataframe pairs"""

    SCHEMA_ACT_INDEX = {
        "id": str,
        "n_points": pl.UInt32,
        "start_time": pl.Datetime,
        "end_time": pl.Datetime,
        "mid_long": pl.Float64,
        "mid_lat": pl.Float64,
    }
    act_index = {k: [] for k in SCHEMA_ACT_INDEX.keys()}
    for a_id in acts.keys():
        act_index["id"].append(a_id)
        act_index["n_points"].append(len(acts[a_id]))
        start = acts[a_id][0, "time"]
        end: pl.Datetime = acts[a_id][-1, "time"]
        act_index["start_time"].append(start)
        act_index["end_time"].append(end)
        act_index["mid_long"].append(acts[a_id]["long"].mean())
        act_index["mid_lat"].append(acts[a_id]["lat"].mean())

    act_index = pl.from_dict(act_index, schema=SCHEMA_ACT_INDEX)
    act_index = act_index.with_columns(
        (pl.col("end_time") - pl.col("start_time")).alias("duration")
    )
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


def load_parquet(filepath: str, cols_required: set = None):
    """Load a parquet file.

    ## Parameters
    - filepath (str)
    - cols_required (set): Raise ValueError if column missing/of null type.

    ## Returns
    - Dataframe (pl.DataFrame)
    """
    if cols_required:
        lazy = pl.scan_parquet(filepath)  # TODO: read_parquet_schema better?
        for col in cols_required:
            if col not in lazy.columns:
                raise ValueError(f"missing column {col}")
            if lazy.schema[col] == pl.Null:
                raise ValueError(f"column {col} of Null type")
        return lazy.collect()
    else:
        return pl.read_parquet(filepath)


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
    - metadata (dict)
    - points (dict)
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
    metadata = {}

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
                        metadata["sport_spec"] = sport_name
                        metadata["sport_main"] = sport_main

        return metadata, points


def find_importable(folder: str, extensions=IMPORT_TYPES):
    """Find all files that could be imported as activities."""

    matches = []
    for root, _, filenames in os.walk(folder):
        for extension in extensions:
            for filename in fnmatch.filter(filenames, f"*{extension}"):
                name = filename.split(".")[0]
                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                matches.append((name, file_path, file_size, extension))

    if not matches:
        return None

    df = pl.DataFrame(matches)
    df.columns = ["name", "path", "size", "type"]
    return df.sort("name", "type")


def convert_fit_polars(filepath):
    """Load a fit file to a dict of metadata and a dataframe of points.

    ## Returns
    - metadata (dict):
    - points (pl.DataFrame):
    """

    act_id = os.path.split(filepath)[-1].split(".")[0]
    metadata, points = load_fit(filepath)
    metadata["id"] = act_id

    points = pl.DataFrame(points)
    points = points.with_columns(points["hr"].cast(pl.UInt16))
    return metadata, points


def convert_all_fit_polars(
    folder_in: str, folder_out: str, overwrite=False, verbose=True
):
    files = find_importable(folder_in, extensions=[".fit", ".fit.gz"])["path"]
    for i, fp in enumerate(files):
        act_id = os.path.split(fp)[-1].split(".")[0]
        path_out = os.path.join(folder_out, act_id + ".parquet")

        skip = False
        if (not overwrite) and os.path.exists(path_out):
            skip = True

        if verbose:
            print(f"{i+1:5d}/{len(files)}: {act_id}", "(skip)" * skip)

        if not skip:
            metadata, points = convert_fit_polars(fp)
            safe_save(points, path_out, overwrite, check_read=True)
            safe_save(
                metadata,
                os.path.join(folder_out, act_id + "_meta.json"),
                overwrite,
                check_read=True,
            )


def safe_save(obj, filepath: str, overwrite=True, check_read=False):
    """Safely save data as file.

    ## Parameters
    - obj (pl.Dataframe|dict|list)
    - filepath (str): destination file including extension
    - overwrite (bool): allow replacing files with same name
    - check_read (bool): read file after saving and check equal to obj.

    """

    if (not overwrite) and os.path.exists(filepath):
        raise FileExistsError("file exists, overwrite not enabled")

    # Save dataframe
    if isinstance(obj, pl.DataFrame) and filepath[-7:] == "parquet":
        # save temporary
        with open(filepath + ".tmp", "wb") as f:
            obj.write_parquet(f)

        os.replace(filepath + ".tmp", filepath)

        if check_read:
            with open(filepath, "rb") as f:
                test = pl.read_parquet(f)
            if not obj.equals(test):
                raise OSError("File read check failed.")
        return True
    # Save JSON
    elif isinstance(obj, (dict, list)) and filepath[-4:] == "json":
        # save temporary
        with open(filepath + ".tmp", mode="w", encoding="utf8") as f:
            json.dump(obj, f, default=serialize_json, indent=4)

        os.replace(filepath + ".tmp", filepath)

        if check_read:
            with open(filepath, encoding="utf8") as f:
                test = json.load(f)
            if not obj == test:
                raise OSError("File read check failed.")
        return True
    else:
        return NotImplemented
