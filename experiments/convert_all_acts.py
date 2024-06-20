from app_functions.activity import Act

from app_functions import data_functions as dataf
import os


folder_in = os.path.join("data", "activities")
folder_parquet = os.path.join("data", "points_parquet")

# TODO This crashes on not a FIT file
# dataf.convert_all_activities_json(
#     folder_in,
#     folder_json,
#     overwrite=False,
#     compress=False,
#     verbose=True,
# )

files = dataf.find_importable(folder_in, [".fit"])

print(files)


dataf.convert_all_fit_polars(folder_in, folder_parquet)
