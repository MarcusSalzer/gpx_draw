import os
import fnmatch
import glob
from timeit import timeit
import pandas as pd

folder = "data"
extensions = [".gpx", ".fit", ".fit.gz", ".json", ".json.gz"]


def find_files_os(folder, extensions):
    matches = []
    for root, dirnames, filenames in os.walk(folder):
        for extension in extensions:
            for filename in fnmatch.filter(filenames, f"*{extension}"):
                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                matches.append((file_path, file_size, extension))
    return pd.DataFrame(sorted(matches), columns=["path", "size", "type"])


def find_files_glob(folder, extensions):
    matches = []
    for extension in extensions:
        pattern = os.path.join(folder, "**", f"*{extension}")
        for file_path in glob.glob(pattern, recursive=True):
            file_size = os.path.getsize(file_path)
            matches.append((file_path, file_size, extension))
    return pd.DataFrame(sorted(matches), columns=["path", "size", "type"])


N_test = 10
os_time = (
    timeit(lambda: find_files_os(folder, extensions), number=N_test) / N_test
)
glob_time = (
    timeit(lambda: find_files_glob(folder, extensions), number=N_test) / N_test
)

print(f"os with fnmatch time: {os_time:.6f} seconds")
print(f"glob time: {glob_time:.6f} seconds")

print(find_files_os(folder, extensions).equals(find_files_glob(folder, extensions)))
print()

# print(find_files_os(folder, extensions))
# print(find_files_glob(folder, extensions))

print(find_files_os(folder, extensions).type.value_counts())
print(find_files_glob(folder, extensions).type.value_counts())
