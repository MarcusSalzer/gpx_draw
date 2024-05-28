## try making a small dash app


import os

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash_bootstrap_templates import load_figure_template

import data_functions as dataf
import plot_functions as plotf
import ui_functions as uif
from ui_functions import make_activity_list, make_main_greeting, make_settings

activity_index = dataf.load_act_index(os.path.join("data", "activity_index.json"))


# loads the "darkly" template and sets it as the default
load_figure_template("darkly")
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.DARKLY])

info_md = make_main_greeting(activity_index)
main_sum_plot = plotf.summary_plot(activity_index)

activity_list = make_activity_list(activity_index)


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
                    config={"scrollZoom": True},
                ),
                type="default",
            ),
        ),
        dbc.Col(html.Div(children=activity_list)),
    ]
)
# row2 = dbc.Row(dcc.Markdown(children="Something...", id="changed"))

settings_page = make_settings()


tabs = dcc.Tabs(
    [
        dcc.Tab(
            label="Summary",
            children=[info_md, dcc.Graph(figure=main_sum_plot, id="main-sum-plot")],
        ),
        dcc.Tab(label="Activities", children=row1),
        dcc.Tab(label="Settings", children=settings_page),
    ]
)

dark_light_toggle = uif.make_dark_light_switch()

app.layout = [html.Div(tabs)]


if __name__ == "__main__":
    app.run(debug=True)