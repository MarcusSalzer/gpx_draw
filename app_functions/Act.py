
import gpxpy
import gpxpy.gpx
import pandas as pd
from plotly import express as px


class Act:
    """Object representing an activity with one track and some metadata"""

    def __init__(
        self, name: str, metadata: dict = None, points: pd.DataFrame = None
    ) -> None:
        self.name = name
        self.metadata = metadata
        self.points = points

    def __str__(self) -> str:
        lines = [self.name, str(len(self.points))]

        return "\n".join(lines)

    @classmethod
    def from_gpxpy(cls, gpx: gpxpy.gpx.GPX):
        assert (
            gpx.tracks and gpx.tracks[0].segments and gpx.tracks[0].segments[0].points
        ), "Incompatible GPX"

        track = gpx.tracks[0]

        # extract metadata
        act_info = cls.info_from_gpx_track(track)

        points = gpx.tracks[0].segments[0].points

        points_df = pd.DataFrame.from_dict(
            {
                "lon": [p.longitude for p in points],
                "lat": [p.latitude for p in points],
                "elev": [p.elevation for p in points],
                "time": [p.time for p in points],
            },
        )

        return cls(metadata=act_info, points=points_df)

    def plot_trace(self, show_grid=False):
        """Plot a trace of the activity."""
        fig = px.line(self.points, x="long", y="lat")

        fig.update_layout(
            title=self.name,
            showlegend=False,
            dragmode="pan",
        )
        fig.update_yaxes(scaleanchor="x", scaleratio=1)

        fig.update_xaxes(showgrid=show_grid)
        fig.update_yaxes(showgrid=show_grid)

        return fig
