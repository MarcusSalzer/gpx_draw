from app_functions.activity import Act

from app_functions import data_functions as dataf
import os

folder_in = os.path.join("data", "activities")
folder_out = os.path.join("data", "activities_json")

#TODO This crashes on not a FIT file
dataf.convert_all_activities_json(
    folder_in,
    folder_out,
    overwrite=False,
    compress=False,
    verbose=True,
)


