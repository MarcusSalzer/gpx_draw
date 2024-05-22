import json
import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import dash_bootstrap_components as dbc



data = {
    "ticker": ["AAPL", "MSFT", "AMZN", "GOOGL"],
    "company": ["Apple", "Microsoft", "Amazon", "Alphabet"],
    "price": [154.99, 268.65, 100.47, 96.75],
    "buy": ["Buy" for i in range(4)],
}
df = pd.DataFrame(data)

columnDefs = [
    {
        "headerName": "Stock Ticker",
        "field": "ticker",
    },
    {"headerName": "Company", "field": "company"},
    {
        "headerName": "Last Close Price",
        "type": "rightAligned",
        "field": "price",
        "valueFormatter": {"function": """d3.format("($,.2f")(params.value)"""},
    },
    {
        "field": "buy",
        "cellRenderer": "DBC_Button_Simple",
    },
]


grid = dag.AgGrid(
    id="act-list-grid",
    columnDefs=columnDefs,
    rowData=df.to_dict("records"),
    columnSize="autoSize",
)


app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Markdown("Example of cellRenderer with custom dash-bootstrap-components Button "),
        grid,
        html.Div(id="changed"),
    ]
)


@callback(
    Output("changed", "children"),
    Input("act-list-grid", "cellRendererData"),
)
def showChange(n):
    return json.dumps(n)


if __name__ == "__main__":
    app.run(debug=True)


"""
Put the following in the dashAgGridComponentFunctions.js file in the assets folder

---------------

var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.DBC_Button_Simple = function (props) {
    const {setData, data} = props;

    function onClick() {
        setData();
    }
    return React.createElement(
        window.dash_bootstrap_components.Button,
        {
            onClick,
            color: props.color,
        },
        props.value
    );
};


"""
