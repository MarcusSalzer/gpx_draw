# A smaller dash app only for viewing dataset properties

import json
import os
from datetime import datetime

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import polars as pl
from dash import (
    Dash,
    Input,
    Output,
    Patch,
    callback,
    dcc,
    exceptions,
    html,
)
from dash_bootstrap_templates import load_figure_template

import app_functions.data_functions as dataf
import app_functions.plot_functions as plotf
import app_functions.stats_functions as statsf

app = Dash(__name__)

PLOT_CONFIG = {
    "scrollZoom": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["select", "autoScale"],
}

ACTIVITY_DF_DIR = os.path.join("data", "points_parquet")

found_files = dataf.find_importable("data", dataf.IMPORT_TYPES)
file_counts = found_files["type"].value_counts()
print(file_counts)

act_index = dataf.load_parquet(
    "data/activity_index.parquet", cols_required={"id", "n_points", "start_time"}
)


lines = [
    f"""{file_counts[k,"type"]}: {file_counts[k,"count"]}"""
    for k in range(len(file_counts))
]

main_info = dcc.Markdown(children="## Found \n\n" + "\n\n".join(lines))

display_selected = dcc.Markdown(children=None, id="display-select")

act_info = dcc.Loading(
    children=html.Div(children="select an activity"), id="current-act-info"
)

summary_month = statsf.summary_month(act_index)

round_plot = dcc.Graph(
    figure=plotf.polar_summary_month(summary_month), config=PLOT_CONFIG
)


def make_act_summary(index_row):
    act_id = index_row["id"]
    n_points = index_row["n_points"]
    start_time = index_row["start_time"]
    duration = index_row["duration"]

    act_df = dataf.load_parquet(os.path.join(ACTIVITY_DF_DIR, act_id + ".parquet"))

    title = html.H1(children="Activity")
    act_df_grid = dag.AgGrid(
        id="grid-current",
        rowData=act_df.to_pandas().to_dict("records"),
        columnDefs=[{"field": i} for i in act_df.columns],
    )

    act_info = html.Div(
        children=[
            title,
            act_df_grid,
        ]
    )
    return act_info


def make_act_list(act_index):
    data = act_index.with_columns(pl.col("start_time").alias("date")).drop(
        "start_time", "end_time"
    )

    # tp parse datetimes
    date_obj = "d3.utcParse('%Y-%m-%dT%H:%M:%S%Z')(params.data.date)"

    grid = dag.AgGrid(
        id="grid-acts",
        rowData=data.to_pandas().to_dict("records"),
        columnDefs=[
            {"field": "id"},
            {"field": "n_points"},
            {
                "field": "date",
                "valueFormatter": {
                    "function": f"d3.timeFormat('%Y-%m-%d %H:%M:%S')({date_obj})"
                },
            },
        ],
    )
    return grid


act_list_grid = make_act_list(act_index)


@callback(
    Output("current-act-info", "children"),
    Input("grid-acts", "cellClicked"),
)
def display_cell_clicked_on(cell):
    if cell:
        return make_act_summary(act_index.row(int(cell["rowId"]), named=True))
    return None


app.layout = html.Div([main_info, act_list_grid, act_info, round_plot])

if __name__ == "__main__":
    print(act_index.head())
    app.run(debug=True)
