# Experiments

Some different experiments...

## Data loading

We want to find a convenient format for loading data. It should be fast so that the user can see many activities quickly.

### Finding files

In order to find files for import we search a directory and its sub-directories. The test directory contains 1495 files of 4 different types. Two methods compared:

-   `fnmatch` : 69ms
-   `glob` : 91ms

### Load single activity

Comparison of file formats for the activity "10022032783", average of 10 trials.

-   Note: `.json` version here only contains points (6 dimensional) and a few string fields, whereas the `.fit` contains more metadata.

| Format     | File size | Load time | Save time |
|------------|-----------|-----------|-----------|
| `.fit`     | 263kB     | 840ms     | N/A       |
| `.fit.gz`  | 128kB     | 920ms     | N/A       |
| `.json`    | 528kB     | 10ms      |           |
| `.json.gz` | 106kB     | 10ms      |           |

**Conclusion**: `json` file (especially compressed) looks promising.

### Loading many activities

Loading time for 1100 activities (a total of 1 862 000 points)

| format                                   | total file size | load time | save time |
|------------------------|----------------|----------------|----------------|
| 1100 `.json` files                       | 220 MB          | 5s        | 24s       |
| 1100 `.json.gz` files                    | 41 MB           | 6s        | 54s       |
| 1100 `.json` files (pandas, points only) | 151 MB          | 9s        | 13s       |
| 1 combined `.json` file                  | 220 MB          | 5s        | 23s       |
| 1 combined `.json.gz` file               | 41 MB           | 5s        | 49s       |

**Conclusion**: Loading compressed files is not a problem, but saving them takes time. Separate files, or one combined doesn't matter (for now)

### Conversions

The activity data is handled as one index containing metadata for all activities, and one data frame of points for each activity.

## Indexing