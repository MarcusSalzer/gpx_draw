import os

import flet as ft
from flet.plotly_chart import PlotlyChart

from app_functions import data_functions as dataf
from app_functions import plot_functions as plotf
from app_functions import stats_functions as statsf

ACT_DIR = os.path.join("data", "points_parquet")
INDEX_PATH = os.path.join("data", "activity_index.parquet")


def main(page: ft.Page):
    print("window", page.width)

    act_index = dataf.load_parquet(INDEX_PATH)
    summary = statsf.summary_interval(act_index, "1mo")
    fig_summary = plotf.summary_hist(summary)

    listview = ft.ListView(
        expand=1,
        spacing=10,
        padding=20,
    )

    for row in act_index.iter_rows(named=True):
        tile = ft.ListTile(
            title=ft.Text(f"act: {row['id']}"),
            subtitle=ft.Text(f"length: {row['length']}"),
        )
        listview.controls.append(tile)



    # Create two columns, each with a width of 50%
    col1 = ft.Column(
        width=page.width / 2,
        controls=[
            PlotlyChart(fig_summary),
            # Add more controls as needed
        ],
    )

    col2 = ft.Column(
        width=page.width / 2,
        controls=[
            listview,
            # Add more controls as needed
        ],
    )

    # Create a row to contain the two columns
    row = ft.Row(
        controls=[col1, col2],
        expand=True,  # Ensure the row takes up the full width of the screen
        spacing=0,  # No spacing between columns
    )

    # Add the row to the page
    page.add(row)

    # Set up the resize event
  
# Start the Flet app
ft.app(target=main)
