import os
import fnmatch
import glob
from timeit import timeit
import pandas as pd
from app_functions import data_functions as dataf

folder = "data"
extensions = [".gpx", ".gpx.gz", ".fit", ".fit.gz", ".json", ".json.gz"]


find_files_fnmatch = dataf.find_importable


def find_files_glob(folder, extensions):
    matches = []
    for extension in extensions:
        pattern = os.path.join(folder, "**", f"*{extension}")
        for file_path in glob.glob(pattern, recursive=True):
            file_size = os.path.getsize(file_path)
            matches.append((file_path, file_size, extension))
    return pd.DataFrame(sorted(matches), columns=["path", "size", "type"])


N_test = 10
os_time = timeit(lambda: find_files_fnmatch(folder, extensions), number=N_test) / N_test
glob_time = timeit(lambda: find_files_glob(folder, extensions), number=N_test) / N_test
print("time listdir", timeit(lambda: os.listdir(folder), number=N_test) / N_test)

print(f"fnmatch time: {os_time:.6f} seconds")
print(f"glob time: {glob_time:.6f} seconds")

print(
    "df equality?",
    find_files_fnmatch(folder, extensions).equals(find_files_glob(folder, extensions)),
)
print()

# print(find_files_os(folder, extensions))
# print(find_files_glob(folder, extensions))

print(find_files_fnmatch(folder, extensions).type.value_counts())
print(find_files_glob(folder, extensions).type.value_counts())

