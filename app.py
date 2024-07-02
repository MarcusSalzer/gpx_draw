import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc


app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

info_store = html.Div(
    [html.H3("output", className="title"), dcc.Markdown("output...", id="info-store")]
)

main_div = html.Div(
    children=dash.page_container,
    style={"padding": "50px"},
)


app.layout = html.Div(
    [
        dcc.Store(id="store", data={}),
        html.Div(
            [
                html.Div(
                    dcc.Link(
                        f"{page['name']} - {page['path']}", href=page["relative_path"]
                    )
                )
                for page in dash.page_registry.values()
            ]
        ),
        html.Hr(style={"color": "red"}),
        main_div,
        info_store,
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
