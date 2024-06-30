## try making a small dash app

import os

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

import app_functions.data_functions as dataf
import app_functions.plot_functions as plotf
import app_functions.ui_functions_old as uif


PLOT_CONFIG = {
    "scrollZoom": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["select", "autoScale"],
}


activity_index = dataf.load_act_index(os.path.join("data", "activity_index.json"))


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

info_md = uif.make_main_greeting(activity_index)

activity_list = uif.make_activity_list(activity_index)


# find latest activity to show it
latest_act_file = max(
    activity_index["activities"],
    key=lambda act: activity_index["activities"][act]["time_start"],
)
latest_act = dataf.load_one_gpx(os.path.join("data", "activities", latest_act_file))
overview_fig = plotf.plot_one_gpx(latest_act)


row1 = dbc.Row(
    [
        dbc.Col(
            dcc.Loading(
                dcc.Graph(
                    id="fig-act-overview",
                    figure=overview_fig,
                    config=PLOT_CONFIG,
                ),
                type="default",
            ),
        ),
        dbc.Col(html.Div(children=activity_list)),
    ]
)

settings_page = uif.make_settings()


tabs = dcc.Tabs(
    [
        dcc.Tab(label="Activities", children=row1),
        dcc.Tab(label="Settings", children=settings_page),
    ]
)

dark_light_toggle = uif.make_dark_light_switch()

app.layout = [html.Div(tabs)]


if __name__ == "__main__":
    app.run(debug=True)
