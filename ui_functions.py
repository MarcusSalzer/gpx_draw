import dash_ag_grid as dag
from dash import Input, Output, html, dcc, callback


def make_activity_list(act_index: dict) -> dag.AgGrid:
    """Create an example list."""
    col_names = [{"field": "name"}, {"field": "length"}, {"field": "date"}]

    row_data = []
    for act in act_index["activities"].values():
        row_info = dict(
            name=act["name"],
            length="%.2f" % (act["length2d_m"] / 1000) + " km", 
            date=act["time_start"].split()[0],
        )
        row_data.append(row_info)

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
