## try making a small dash app

import json

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

from data_functions import load_all_gpx, plot_one_gpx, summary_plot
from ui_functions import make_activity_list, make_main_greeting, make_settings


activities = load_all_gpx("data/activities", sample=3)
print("loaded activities")

fig_overview = plot_one_gpx(activities[0])  # .update_layout(width=600, height=400)


with open("data/activity_index.json") as f:
    activity_index: dict = json.load(f)


activity_list = make_activity_list(activity_index)
info_md = make_main_greeting(act_index=activity_index)

main_sum_plot = summary_plot(activity_index)


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

div_block_style = dict(width="49%", display="inline-block")


row1 = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(
                id="fig_act_overview", figure=fig_overview, config={"scrollZoom": True}
            ),
            style=div_block_style,
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
