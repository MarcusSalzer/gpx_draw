import os
from datetime import datetime
import polars as pl

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
    Patch,
    callback,
    dcc,
    exceptions,
    html,
)

STYLES = {
    "button": {
        "padding": "5px",
        "margin": "10px",
    },
    "searchbar": {
        "padding": "10px",
        "margin": "0px",
        "width": "100%",
        "height": "40px",
    },
}


def main_greeting(act_index: pl.DataFrame = None) -> dcc.Markdown:
    now = datetime.now()

    if 5 <= now.hour < 11:
        greeting = "Good morning"
    elif 13 <= now.hour < 17:
        greeting = "Good afternoon"
    elif 17 <= now.hour < 21:
        greeting = "Good evening"
    elif 22 <= now.hour < 25:
        greeting = "Good night"
    else:
        greeting = "Hello"

    lines = [
        f"# {greeting}",
        "This is a **prototype** ``dash`` app.",
    ]

    if act_index is not None:
        n_act = len(act_index)
        total_len = act_index["length"].sum()

        lines.append(f"- You have {n_act} activities.")
        lines.append("    - Total distance %.1f km." % (total_len / 1000))

    info_md = dcc.Markdown(children="\n ".join(lines))
    return info_md


def activity_list(act_index: pl.DataFrame) -> html.Div:
    """Create a list of all activities."""

    data = act_index.with_columns(pl.col("start_time").alias("date")).drop(
        "start_time", "end_time"
    )
    # to parse datetimes
    date_obj = "d3.utcParse('%Y-%m-%dT%H:%M:%S%Z')(params.data.date)"

    grid = dag.AgGrid(
        id="grid-acts",
        rowData=data.select("id", "n_points", "date", "length", "sport_spec")
        .to_pandas()
        .to_dict("records"),
        columnDefs=[
            {
                "field": "date",
                "valueFormatter": {
                    "function": f"d3.timeFormat('%Y-%m-%d %H:%M:%S')({date_obj})"
                },
            },
            {
                "field": "length",
                "valueFormatter": {"function": "d3.format(',.2f')(params.value/1000)"},
            },
            {"field": "sport_spec"},
            {"field": "n_points"},
            {"field": "id"},
        ],
        columnSize="autoSize",
        defaultColDef={"flex": 1},
        dashGridOptions={"animateRows": True},
        style={"height": "100%"},
    )

    searchbar = dcc.Input(
        id="searchbar-acts", placeholder="search...", style=STYLES["searchbar"]
    )

    div = html.Div(children=[searchbar, grid], style={"height": "100%"})
    return div


@callback(
    Output("grid-acts", "dashGridOptions"),
    Input("searchbar-acts", "value"),
)
def update_activity_filter(filter_value):
    """Callback. Apply a quick filter to activity list"""
    newFilter = Patch()
    newFilter["quickFilterText"] = filter_value
    return newFilter


@callback(
    Output("info-out", "children"),
    Input("grid-acts", "cellClicked"),
)
def display_cell_clicked_on(cell: dict):
    if cell:
        return cell["rowId"]
    return None
