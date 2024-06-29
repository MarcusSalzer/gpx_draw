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


act_index = dataf.load_parquet(
    "data/activity_index.parquet", cols_required={"id", "n_points", "start_time"}
)


summary = statsf.summary_interval(act_index, "1mo")


def make_act_list(act_index):
    data = act_index.with_columns(pl.col("start_time").alias("date")).drop(
        "start_time", "end_time"
    )

    # to parse datetimes
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


def make_summary_grid(summary: pl.DataFrame):
    grid = dag.AgGrid(
        id="grid-acts",
        rowData=summary.to_pandas().to_dict("records"),
        columnDefs=[
            {"field": "date"},
            {"field": "label"},
            {"field": "count"},
        ],
    )
    return grid


# @callback(
#     Output("current-act-info", "children"),
#     Input("grid-acts", "cellClicked"),
# )
# def display_cell_clicked_on(cell):
#     if cell:
#         return make_act_summary(act_index.row(int(cell["rowId"]), named=True))
#     return None


def layout():
    """make all layout components"""

    title = html.H1(children="Summary")
    act_grid = make_act_list(act_index)
    summary_grid = make_summary_grid(summary)

    summary_fig = plotf.summary_hist(summary[-12:])
    summary_plot = dcc.Graph(figure=summary_fig, config={"displayModeBar": False})

    return [title, summary_plot, summary_grid]


app.layout = html.Div(layout())

if __name__ == "__main__":
    print(act_index.columns)
    print(summary.columns)
    app.run(debug=True)
