import dash_ag_grid as dag
from dash import Input, Output, html, dcc, callback


def make_activity_list()->dag.AgGrid:
    """Create an example list."""
    col_names = [
        {"field": "name"},
        {"field": "length"},
    ]
    row_data = [
        {"name": "test1", "length": 1223},
        {"name": "test2", "length": 777},
    ]


    grid = dag.AgGrid(
        id="cellrenderer-grid",
        columnSize="sizeToFit",
        getRowId="params.data.make",
        columnDefs=col_names,
        rowData=row_data,
    )
    return grid



@callback(
    Output("cellrenderer-data", "children"),
    Input("cellrenderer-grid", "cellRendererData"),
)
def show_click_data(data):
    if data:
        return (
            "You selected option {} from the colId {}, rowIndex {}, rowId {}.".format(
                data["value"],
                data["colId"],
                data["rowIndex"],
                data["rowId"],
            )
        )
    return "No menu item selected."
