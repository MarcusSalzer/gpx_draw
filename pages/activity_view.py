import os
import polars as pl

import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
    State,
    callback,
    dcc,
    exceptions,
    html,
    ctx,
    register_page,
)
from plotly import graph_objects as go

from app_functions import data_functions as dataf
from app_functions import stats_functions as statsf
from app_functions import plot_functions as plotf
from app_functions import ui_functions as uif

register_page(__name__)

ACT_DIR = os.path.join("data", "points_parquet")


class Act:
    def __init__(
        self,
        id: str = None,
        act: pl.DataFrame = None,
    ) -> None:
        self.id = id
        self.act_df = act


act = Act()
act_id = None

graph_geo = dcc.Graph(figure=go.Figure(), id="graph-geo")
info_text = html.Div(children="pick an activity...", id="info-act")


def layout():
    return ([info_text, graph_geo])


## CALLBACKS ##


@callback(
    Output("graph-geo", "figure"),
    Output("info-act", "children"),
    Input("store", "data"),
)
def update_current(data: dict):
    if data and data["current_act_id"]:
        act_id_new = data["current_act_id"]

        if act_id_new != act.id:
            act.id = data["current_act_id"]
            act.act_df = dataf.load_parquet(os.path.join(ACT_DIR, act.id + ".parquet"))

            print(act.id)
            fig_act = plotf.plot_points_geo(act.act_df["lat"], act.act_df["long"])
            return [fig_act, act.id]

    raise exceptions.PreventUpdate()
