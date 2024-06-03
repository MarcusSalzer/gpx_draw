# Experiments

Some different experiments...

## Data loading

We want to find a convenient format for loading data. It should be fast so that the user can see many activities quickly.

### Load single activity

Comparison of file formats for the activity "10022032783", average of 10 trials.

-   Note: json version here only contains points and a few string fields

| Format     | File size | Load time | Save time |
|------------|-----------|-----------|-----------|
| `.fit`     | 263kB     | 840ms     | N/A       |
| `.fit.gz`  | 128kB     | 920ms     | N/A       |
| `.json`    | 528kB     | 10ms      |           |
| `.json.gz` | 106kB     | 10ms      |           |

**Conclusion**: `json` files (especially compressed) looks promising.

### Conversions

The activity data is handled as `Act` objects, these can be created from, or converted to a `dict`.