## try making a small dash app

import dash_ag_grid as dag
from dash import Dash, Input, Output, callback, dash_table, dcc, html
import json

from data_functions import load_all_gpx, plot_one_gpx, index_activities
from ui_functions import make_activity_list

activities = load_all_gpx("data/activities", sample=3)
print("loaded activities")

fig_overview = plot_one_gpx(activities[0]).update_layout(width=600, height=400)

info_md = dcc.Markdown("""
# Hello
                       
This is a small prototype of a dash app.
                       
- We need more functions.
""")

with open("data/activity_index.json") as f:
    activity_index = json.load(f)

activity_list = make_activity_list(activity_index)


app = Dash(__name__)

div_block_style = dict(width="49%", display="inline-block")


app.layout = [
    html.Div(children="Hello World"),
    html.Div(dcc.Graph(figure=fig_overview), style=div_block_style),
    html.Div(info_md, style=div_block_style),
    html.Div(
        [
            dcc.Markdown("Example: Row Menu Component"),
            activity_list,
            html.P(id="cellrenderer-data"),
        ]
    ),
]

if __name__ == "__main__":
    app.run(debug=True)
