from functools import cache
from pathlib import Path
from typing import Any, Optional, cast

from holoviews import Curve
from pandas import DataFrame, Series, Timestamp, read_csv


@cache
def read_data() -> DataFrame:
    path = Path("/data/derek/Dropbox/Temporary/owid-covid-data.csv")
    return cast(
        DataFrame,
        read_csv(
            path,
            dtype={"iso_code": "string", "new_cases": "Int64"},
            parse_dates=["date"],
        ),
    )


@cache
def get_new_cases(
    country: str, /, *, start: Any = None, end: Any = None
) -> Series:
    if country == "HKG":
        raise NotImplementedError()
    else:
        data = read_data()
        data = data.loc[data["iso_code"] == country].set_index("date")[
            "new_cases"
        ]
    if start is not None:
        data = data.loc[data.index >= Timestamp(start)]
    if end is not None:
        data = data.loc[data.index <= Timestamp(end)]
    return data


def plot_new_cases(
    country: str,
    /,
    *,
    start: Any = None,
    end: Any = None,
    smooth: Optional[int] = None,
    aspect: float = 2.5,
) -> Series:
    data = get_new_cases(country, start=start, end=end).astype(float)
    if smooth is not None:
        data = data.rolling(smooth).mean()
    return Curve(data).opts(aspect=aspect, show_grid=True)
