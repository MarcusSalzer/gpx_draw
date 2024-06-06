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
        name: str = None,
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

    def __repr__(self) -> str:
        return ", ".join((f"{s}={getattr(self,s)}" for s in self.__slots__))

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, Act):
            return NotImplemented
        for s in self.__slots__:
            if isinstance(getattr(self, s), pd.DataFrame):
                if not getattr(self, s).equals(getattr(obj, s)):
                    return False
            elif getattr(self, s) != getattr(obj, s):
                return False
        return True

    def __str__(self) -> str:
        return f"Act: {self.name}, {len(self.points)} points"

    @classmethod
    def from_gpxpy(cls, gpx: gpxpy.gpx.GPX):
        assert (
            gpx.tracks and gpx.tracks[0].segments and gpx.tracks[0].segments[0].points
        ), "Incompatible GPX"

        track = gpx.tracks[0]

        points = track.segments[0].points

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
        act = Act()

        for s in cls.__slots__:
            if s == "points":
                df = pd.DataFrame.from_dict(d[s])
                df["time"] = pd.to_datetime(df["time"])
                df.reset_index(drop=True, inplace=True)
                setattr(act, s, df)
            else:
                setattr(act, s, d[s])
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
