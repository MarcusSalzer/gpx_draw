import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, callback, Patch
import pandas as pd

import json

with open("data/activity_index.json") as f:
    activity_index = json.load(f)

app = Dash(__name__)

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/ag-grid/olympic-winners.csv"
)


row_data = []
for act in activity_index["activities"].values():
    row_info = {
        "name": act["name"],
        "length (km)": act["length2d_m"] / 1000,
        "date": act["time_start"].split()[0],
    }
    row_data.append(row_info)
df = pd.DataFrame.from_records(row_data)

print(df.head())

col_names = [
    {"field": "name"},
    {
        "field": "length (km)",
        "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
    },
    {"field": "date"},
]

app.layout = html.Div(
    [
        html.Div("Quick Filter:"),
        dcc.Input(id="quick-filter-input", placeholder="filter..."),
        dag.AgGrid(
            id="quick-filter-simple",
            rowData=df.to_dict("records"),
            columnDefs=col_names,
            defaultColDef={"flex": 1},
            dashGridOptions={"animateRows": False},
        ),
    ]
)


@callback(
    Output("quick-filter-simple", "dashGridOptions"),
    Input("quick-filter-input", "value"),
)
def update_filter(filter_value):
    newFilter = Patch()
    newFilter["quickFilterText"] = filter_value
    return newFilter


if __name__ == "__main__":
    app.run(debug=True)
