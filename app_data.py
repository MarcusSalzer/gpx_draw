# A smaller dash app only for viewing dataset properties

import os

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

import app_functions.data_functions as dataf
import app_functions.plot_functions as plotf

app = Dash(__name__)

found_files = dataf.find_importable("data", dataf.IMPORT_TYPES)
file_counts = found_files.type.value_counts()

lines = [f"{k} : {file_counts[k]}" for k in file_counts.index]

div = dcc.Markdown(children="## Found \n\n" + "\n\n".join(lines))

app.layout = div

if __name__ == "__main__":
    app.run(debug=True)
