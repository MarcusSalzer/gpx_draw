## try making a small dash app

import json

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, callback, dash_table, dcc, html

from data_functions import index_activities, load_all_gpx, plot_one_gpx
from ui_functions import make_activity_list, make_main_greeting

activities = load_all_gpx("data/activities", sample=3)
print("loaded activities")

fig_overview = plot_one_gpx(activities[0])  # .update_layout(width=600, height=400)


with open("data/activity_index.json") as f:
    activity_index = json.load(f)

activity_list = make_activity_list(activity_index)
info_md = make_main_greeting(act_index=activity_index)


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

div_block_style = dict(width="49%", display="inline-block")


layout1 = [
    html.Div(children="Hello World"),
    html.Div(
        dcc.Graph(figure=fig_overview, config={"scrollZoom": True}),
        style=div_block_style,
    ),
    html.Div(info_md, style=div_block_style),
    html.Div(
        [
            dcc.Markdown("Example: Row Menu Component"),
            activity_list,
            html.P(id="cellrenderer-data"),
        ]
    ),
]


row1 = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure=fig_overview, config={"scrollZoom": True}),
            style=div_block_style,
        ),
        dbc.Col(html.Div(children=activity_list)),
    ]
)

row2 = dbc.Row(
    html.Div(
        [
            dcc.Markdown("Example: Row Menu Component"),
            html.P(id="cellrenderer-data"),
        ]
    ),
)

tabs = dcc.Tabs(
    [
        dcc.Tab(label="Summary", children=info_md),
        dcc.Tab(label="Activities", children=[row1,row2]),
    ]
)

app.layout = [html.Div(tabs)]

if __name__ == "__main__":
    app.run(debug=True)
