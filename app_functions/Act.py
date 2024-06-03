import gpxpy
import gpxpy.gpx
import pandas as pd
from plotly import express as px, graph_objects as go


class Act:
    """Object representing an activity with one track and some metadata"""

    __slots__ = (
        "name",
        "metadata",
        "points",
        "length2d",
        "length3d",
        "sport",
    )

    # clas-level consts.

    SPORTS = {
        "running": ["trail"],
        "cycling": ["road", "mtb"],
        "hiking": [],
    }

    def __init__(
        self,
        name: str,
        sport: str = None,
        metadata: dict = None,
        points: pd.DataFrame = None,
        length2d: float = None,
        length3d: float = None,
    ) -> None:
        self.name = name
        self.metadata = metadata
        self.points = points
        self.length2d = length2d
        self.length3d = length3d
        self.sport = sport

    def __str__(self) -> str:
        lines = [self.name, str(len(self.points))]

        return "\n".join(lines)

    @classmethod
    def from_gpxpy(cls, gpx: gpxpy.gpx.GPX):
        assert (
            gpx.tracks and gpx.tracks[0].segments and gpx.tracks[0].segments[0].points
        ), "Incompatible GPX"

        track = gpx.tracks[0]

        points = gpx.tracks[0].segments[0].points

        points_df = pd.DataFrame.from_dict(
            {
                "lon": [p.longitude for p in points],
                "lat": [p.latitude for p in points],
                "elev": [p.elevation for p in points],
                "time": [p.time for p in points],
            },
        )

        return cls(metadata=None, points=points_df)

    @classmethod
    def from_dict(cls, d: dict):
        assert set(d.keys()) == set(cls.__slots__), "Invalid keys"
        act = Act(name=d["name"])
        for s in cls.__slots__:
            setattr(act, s, d[s])

        # TODO: PARSE POINTS AS DF: DATETIMES!
        return act

    def to_dict(self) -> dict:
        """Return activity as a dict"""
        d = {s: getattr(self, s, None) for s in self.__slots__}
        return d

    def plot_trace(self, show_grid=False) -> go.Figure:
        """Plot a trace of the activity."""
        p = self.points

        hov_tmp = "<br>".join(
            [
                "time: %{customdata[0]}",
                "alt: %{customdata[1]} m",
            ]
        )
        custom_data = [
            p.time.map(lambda x: x.time()),
            p.alt_enh.map(lambda x: "%.1f" % x),
        ]

        fig = px.line(
            p,
            x="long",
            y="lat",
            custom_data=custom_data,
        )
        fig.update_traces(hovertemplate=hov_tmp)
        fig.update_layout(
            title=self.name,
            showlegend=False,
            dragmode="pan",
            margin=dict(l=20, r=20, t=60, b=20),
        )
        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
            showgrid=show_grid,
            visible=False,
        )
        fig.update_xaxes(showgrid=show_grid, visible=False)

        return fig
