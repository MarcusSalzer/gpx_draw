from dash import Dash, html
import dash_ag_grid as dag
from datetime import datetime
import polars as pl
from app_functions import data_functions as dataf

act_index = dataf.load_parquet("data/activity_index.parquet")
data = act_index.with_columns(pl.col("start_time").alias("date")).drop(
    "start_time", "end_time"
)
print(data)

rowData = data.to_pandas().to_dict("records")

# function to create a date object from  a date string "YYYY-MM-DD"
# date_obj = """d3.timeParse("%Y-%m-%dT%H:%M:%S%Z")(params.data.date)""" 

# if the time is in utc:
date_obj = """d3.utcParse("%Y-%m-%dT%H:%M:%S%Z")(params.data.date)"""


columnDefs = [
    {
        "headerName": "Datetime string",
        "field": "date",
        "filter": False,
    },
    {
        "headerName": "MM/DD/YYYY",
        "valueGetter": {"function": date_obj},
        "valueFormatter": {"function": f"d3.timeFormat('%m/%d/%Y')({date_obj})"},
    },
    {
        "headerName": "Mon DD, YYYY",
        "valueGetter": {"function": date_obj},
        "valueFormatter": {"function": f"d3.timeFormat('%b %d, %Y')({date_obj})"},
    },
    {
        "headerName": "day, Mon DD, YYYY",
        "valueGetter": {"function": date_obj},
        "valueFormatter": {"function": f"d3.timeFormat('%a %b %d, %Y')({date_obj})"},
    },
    {
        "headerName": "yyyy-mm-dd HH:MM:SS tt",
        "valueGetter": {"function": date_obj},
        "valueFormatter": {
            "function": f"d3.timeFormat('%Y-%m-%d %I:%M:%S %p')({date_obj})"
        },
    },
    {
        "headerName": "yyyy-mm-dd hh:mm:ss",
        "valueGetter": {"function": date_obj},
        "valueFormatter": {
            "function": f"d3.timeFormat('%Y-%m-%d %H:%M:%S')({date_obj})"
        },
    },
]

defaultColDef = {
    "filter": "agDateColumnFilter",
    "filterParams": {"buttons": ["clear", "apply"]},
    "sortable": True,
}

app = Dash(__name__)

app.layout = html.Div(
    [
        dag.AgGrid(
            id="d3-value-formatters-datetime-grid",
            columnDefs=columnDefs,
            rowData=rowData,
            defaultColDef=defaultColDef,
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
