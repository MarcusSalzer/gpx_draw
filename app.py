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
    ctx,
)
from dash_bootstrap_templates import load_figure_template

from app_functions import data_functions as dataf
from app_functions import stats_functions as statsf
from app_functions import plot_functions as plotf
from app_functions import ui_functions as uif

PLOT_CONFIG = {
    "scrollZoom": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["select", "autoScale"],
}

act_index = dataf.load_parquet(
    "data/activity_index.parquet", cols_required={"id", "n_points", "start_time"}
)
summary = statsf.summary_interval(act_index, "1mo")

# MOVE to uif? need act index stored in its object????
buttons_summary_interval = html.Div(
    children=[
        html.Button("Yearly", id="bt-int-1y", n_clicks=0, style=uif.STYLES["button"]),
        html.Button("Monthly", id="bt-int-1mo", n_clicks=0, style=uif.STYLES["button"]),
        html.Button("Weekly", id="bt-int-1w", n_clicks=0, style=uif.STYLES["button"]),
    ],
)
info_out = html.Div(
    [html.H3("output", className="title"), dcc.Markdown("output...", id="info-out")]
)

act_list = uif.activity_list(act_index)


@callback(
    Output("graph-summary", "figure"),
    # interval buttons
    Input("bt-int-1y", "n_clicks"),
    Input("bt-int-1mo", "n_clicks"),
    Input("bt-int-1w", "n_clicks"),
)
def update_graph_summary(*args):
    """Callback. Update summary graph."""
    btn_id: str = ctx.triggered_id

    if not btn_id:
        btn_id = "bt-int-1mo"

    # interval button pressed?
    if "-int-" in btn_id:
        interval = btn_id.split("-")[-1]

        summary = statsf.summary_interval(act_index, interval)
        fig_summary = plotf.multi_summary_hist([summary], interval=interval)
        return fig_summary

    raise exceptions.PreventUpdate()


# components
greeting = uif.main_greeting(act_index)
summary_graph = dcc.Graph(
    id="graph-summary",
    figure=plotf.multi_summary_hist([summary], interval="1y"),
    config={"displayModeBar": False, "scrollZoom": True},
)

col_left = dbc.Col(
    children=[
        greeting,
        buttons_summary_interval,
        summary_graph,
        info_out,
    ]
)
col_right = dbc.Col(children=[act_list])
cols = dbc.Row(children=[col_left, col_right])


main_div = html.Div(
    children=cols,
    style={"padding": "50px"},
)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = main_div

if __name__ == "__main__":
    app.run(debug=True)
