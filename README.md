# gpx_draw

Here we are working on a gpx visualization and activity statistics app.

## Features

- Main page with greeting
- Activity view
    - Activity list, search and sort
    - Trace and altitude plot

## todo

- Data
    - import FIT
        - Interesting to find common keys to store as metadata?
    - aliases to standardize sport names
    - NaN in json (problem?)
    - Even faster? polars, msgspec, dask, etc etc,
    - import activity from (naive but reasonable) XML file?
- Summary
    - timeframes: weekly, monthly, yearly, all time
    - interesting stats:
        - cumulative distance (per type?)
        - altitude gain
- Plotting
    - Map projection, will lat/long be distorted?
    - Heatmap
    - first plot only midpoints to show where the acts are.
    - Then user picks a region (automatic suggestions (bb for regions))
- Activities
    - show activity type, dropdown: filter by sport
- Settings
    - enable animation
    - color theme
    - reset ui (affected parts?) on settings changed
- Styling
    - color themes
    - ugly "show" button
