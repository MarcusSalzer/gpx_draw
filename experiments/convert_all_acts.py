from app_functions import data_functions as dataf
import os

folder_in = os.path.join("data", "activities")
folder_parquet = os.path.join("data", "points_parquet")

files = dataf.find_importable(folder_in, [".fit"])
print(files)

dataf.convert_all_fit_polars(folder_in, folder_parquet, overwrite=True)
 