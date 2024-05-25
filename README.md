# gpx_draw

Here we are working on a gpx visualization and activity statistics app.

## Features

- Main page with greeting
- Activity view
    - Activity list, search and sort
    - Trace and altitude plot

## todo

- Summary
    - timeframes: weekly, monthly, yearly, all time
        - plot overview
    - interesting stats:
        - cumulative distance (per type?)
        - altitude gain
        - Eddington number
- Activities
    - loading activity on selection
        - needs to be fast. Convert gpx tracks to faster format (csv?) load pandas/polars?
        - custom component? 
        - loading indicator
    - show activity type
- Settings
    - enable animation
    - color theme
- Styling
    - color themes
    - ugly "show" button
