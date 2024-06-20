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
from dash_bootstrap_templates import load_figure_template

import app_functions.data_functions as dataf
import app_functions.plot_functions as plotf
import app_functions.stats_functions as statsf

# adds  templates to plotly.io
load_figure_template(["minty", "minty_dark"])

SETTINGS_PATH = os.path.join("data", "settings.json")

activity_index = dataf.load_act_index(os.path.join("data", "activity_index.json"))
settings_dict = dataf.load_json(SETTINGS_PATH)


def make_main_greeting(act_index: dict = None) -> dcc.Markdown:
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

    if act_index:
        n_act = len(act_index["activities"])
        total_len = sum(act["length2d_m"] for act in act_index["activities"].values())
        updated: datetime = act_index["updated"]

        lines.append(f"- You have {n_act} activities.")
        lines.append("    - Total distance %.1f km." % (total_len / 1000))
        lines.append("\nAll time, all activity E=%d" % statsf.eddington_nbr_old(act_index))
        lines.append(f"\n*Last updated {updated.date()}*")

    info_md = dcc.Markdown(children="\n ".join(lines), style={"padding": "50px"})
    return info_md


def make_activity_list(act_index: dict) -> dag.AgGrid:
    """Create an example list."""
    col_names = [
        {
            "field": "show",
            "cellRenderer": "DBC_Button_Simple",
        },
        {"field": "name"},
        {
            "field": "length (km)",
            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
        },
        {"field": "date"},
    ]

    row_data = []
    for act in act_index["activities"].values():
        row_info = {
            "name": act["name"],
            "length (km)": act["length2d_m"] / 1000,
            "date": act["time_start"].date(),
            "show": "show",
        }
        row_data.append(row_info)

    grid = dag.AgGrid(
        id="act-list-grid",
        columnSize="autoSize",
        columnDefs=col_names,
        rowData=row_data,
        defaultColDef={"flex": 1},
        dashGridOptions={"animateRows": settings_dict["animate_ui"]},
    )
    searchbar = dcc.Input(id="act-list-search", placeholder="search...")

    div = html.Div(children=[searchbar, grid])
    return div


@callback(
    Output("act-list-grid", "dashGridOptions"),
    Input("act-list-search", "value"),
)
def update_activity_filter(filter_value):
    """Callback. Apply a quick filter to activity list"""
    newFilter = Patch()
    newFilter["quickFilterText"] = filter_value
    return newFilter


@callback(
    Output("fig-act-overview", "figure"),
    Input("act-list-grid", "cellRendererData"),
)
def change_plot(n):
    """Callback. Update the activity overview plot when selected from list."""
    if not n:
        raise exceptions.PreventUpdate()

    idx = int(n["rowId"])
    filename = list(activity_index["activities"].keys())[idx]
    gpx = dataf.load_one_gpx(os.path.join("data", "activities", filename))

    return plotf.plot_one_gpx(gpx)


def make_settings():
    """make settings page"""
    components = [
        html.H1("Settings", className="title"),
        dcc.Checklist(
            options=["animate_ui"],
            id="checklist-settings",
            value=[
                k
                for k in settings_dict.keys()
                if (settings_dict[k] and isinstance(settings_dict[k], bool))
            ],
        ),
        dcc.Markdown("settings take effect after restart (as of now)"),
    ]
    return html.Div(components, style={"padding": "20px"})


@callback(
    Input("checklist-settings", "value"),
)
def update_settings_checklist(val):
    # update settings dict
    for k in settings_dict.keys():
        if isinstance(settings_dict[k], bool):
            if k in val:
                settings_dict[k] = True
            else:
                settings_dict[k] = False

    dataf.save_settings(SETTINGS_PATH, settings_dict)


def make_dark_light_switch():
    return html.Span(
        [
            dbc.Label(className="fa fa-moon", html_for="switch"),
            dbc.Switch(
                id="switch",
                value=True,
                className="d-inline-block ms-1",
                persistence=True,
            ),
            dbc.Label(className="fa fa-sun", html_for="switch"),
        ]
    )


# @callback(
#     Output("main-sum-plot", "figure"),
#     Input("switch", "value"),
# )
# def update_figure_template(switch_on):
#     # When using Patch() to update the figure template, you must use the figure template dict
#     # from plotly.io  and not just the template name
#     template = pio.templates["minty"] if switch_on else pio.templates["minty_dark"]

#     patched_figure = Patch()
#     patched_figure["layout"]["template"] = template
#     return patched_figure


# clientside_callback(
#     """
#     (switchOn) => {
#        document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');
#        return window.dash_clientside.no_update
#     }
#     """,
#     Output("switch", "id"),
#     Input("switch", "value"),
# )
