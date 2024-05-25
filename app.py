## try making a small dash app

import json

from dash.development.base_component import Component
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

from data_functions import load_one_gpx, plot_one_gpx, summary_plot
from ui_functions import make_activity_list, make_main_greeting, make_settings

with open("data/activity_index.json") as f:
    activity_index: dict = json.load(f)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

info_md = make_main_greeting(activity_index)
main_sum_plot = summary_plot(activity_index)

activity_list = make_activity_list(activity_index)

# TODO: display most recent activity first

overview_fig = plot_one_gpx()


row1 = dbc.Row(
    [
        dbc.Col(
            dcc.Loading(
                dcc.Graph(
                    id="fig_act_overview",
                    figure=overview_fig,
                    config={"scrollZoom": True},
                ),
                type="default",
            ),
        ),
        dbc.Col(html.Div(children=activity_list)),
    ]
)
row2 = dbc.Row(dcc.Markdown(children="Something...", id="changed"))

settings_page = html.Div(
    children=[dcc.Markdown(children="# Settings"), make_settings()]
)


tabs = dcc.Tabs(
    [
        dcc.Tab(label="Summary", children=[info_md, dcc.Graph(figure=main_sum_plot)]),
        dcc.Tab(label="Activities", children=[row1, row2]),
        dcc.Tab(label="Settings", children=settings_page),
    ]
)

app.layout = [html.Div(tabs)]


if __name__ == "__main__":
    app.run(debug=True)
