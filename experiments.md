# Experiments

Some different experiments...

## Data loading

We want to find a convenient format for loading data. It should be fast so that the user can see many activities quickly.

### Load single activity

Comparison of file formats for the activity "10022032783", average of 10 trials.

-   Note: json version here only contains points and a few string fields

| Format     | File size | Load time |
|------------|-----------|-----------|
| `.fit`     | 263kB     | 0.84s     |
| `.fit.gz`  | 128kB     | 0.92s     |
| `.json`    | 528kB     | 0.01s     |
| `.json.gz` | 106kB     | 0.01s     |

**Conclusion**: `json` files (especially compressed) looks promising.