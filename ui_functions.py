import dash_ag_grid as dag
from dash import Input, Output, html, dcc, callback
from datetime import datetime


def make_main_greeting(act_index: dict = None) -> dcc.Markdown:
    now = datetime.now()

    if 5 <= now.hour < 11:
        greeting = "Good morning"
    elif 13 <= now.hour < 17:
        greeting = "Good afternoon"
    elif 17 <= now.hour < 21:
        greeting = "Good evening"
    else:
        greeting = "Hello"

    lines = [
        f"# {greeting}",
        "This is a **prototype** ``dash`` app.",
    ]

    if act_index:
        n_act = len(act_index["activities"])
        total_len = sum(act["length2d_m"] for act in act_index["activities"].values())
        updated = act_index["updated"]

        lines.append(f"- You have {n_act} activities.")
        lines.append("    - Total distance %.2f km."%(total_len/1000))
        lines.append(f"\n*Last updated {updated}*")


    info_md = dcc.Markdown(children="\n ".join(lines), style={"padding": "50px"})
    return info_md


def make_activity_list(act_index: dict) -> dag.AgGrid:
    """Create an example list."""
    col_names = [
        {"field": "name"},
        {
            "field": "length (km)",
            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
        },
        {"field": "date"},
    ]

    row_data = []
    for act in act_index["activities"].values():
        row_info = {
            "name": act["name"],
            "length (km)": act["length2d_m"] / 1000,
            "date": act["time_start"].split()[0],
        }
        row_data.append(row_info)

    grid = dag.AgGrid(
        id="cellrenderer-grid",
        className="ag-theme-alpine",
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
