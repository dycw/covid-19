from collections.abc import Iterable
from functools import cache
from functools import reduce
from operator import add
from typing import Any
from typing import Optional
from typing import cast

from holoviews import Curve
from holoviews import Overlay
from pandas import NA
from pandas import DataFrame
from pandas import Series
from pandas import read_csv
from pandas import to_datetime
from requests import get


# data


@cache
def download_data_hkg() -> DataFrame:
    url = "https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Flatest_situation_of_reported_cases_covid_19_eng.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%7D"  # noqa: E501
    response = get(url)
    df = DataFrame.from_records(response.json())
    df["As of date"] = [
        to_datetime(x, format="%d/%m/%Y") for x in df["As of date"]
    ]
    for name, col in df.items():
        if isinstance(name, str) and name.startswith("Number of"):
            df[name] = Series(
                [x if x != "" else NA for x in col], dtype="Int64"
            )
    return df


@cache
def download_data_owid() -> DataFrame:
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    return read_csv(
        url,
        dtype={"iso_code": "string", "new_cases": "Int64"},
        parse_dates=["date"],
    )


def _get_new_cases_hkg() -> Series:
    df = download_data_hkg().set_index("As of date")
    series = df["Number of confirmed cases"]
    name = "Number of cases tested positive for SARS-CoV-2 virus"
    return series.where(series.notna(), other=df[name]).diff()


def _get_new_cases_owid(country: str, /) -> Series:
    df = download_data_owid()
    return df.loc[df["iso_code"] == country].set_index("date")["new_cases"]


def get_new_cases(
    country: str, /, *, start: Any = None, end: Any = None
) -> Series:
    if country == "HKG":
        data = _get_new_cases_hkg()
    else:
        data = _get_new_cases_owid(country)
    if start is not None:
        data = cast(Series, data.loc[data.index >= to_datetime(start)])
    if end is not None:
        data = cast(Series, data.loc[data.index <= to_datetime(end)])
    return data.rename(country)


_DEFAULT_ASPECT = 2.5


def plot_new_cases(
    country: str,
    /,
    *,
    scale: Optional[int] = None,
    start: Any = None,
    end: Any = None,
    smooth: Optional[int] = None,
    aspect: float = _DEFAULT_ASPECT,
) -> Series:
    data = get_new_cases(country, start=start, end=end).astype(float)
    if scale is None:
        vdim_label = "New cases"
    else:
        data = data / (10 ** scale)
        vdim_label = scale * "0"
        vdim_label = f"New cases ({vdim_label})"
    if smooth is not None:
        data = data.rolling(smooth).mean()
    return Curve(
        data=(data.index, data.values),
        kdims=["date"],
        vdims=[(f"new_cases_{country}", vdim_label)],
        label=country,
    ).opts(aspect=aspect, show_grid=True, tools=["hover"])


def get_combined_plot(
    countries_and_scales: Iterable[tuple[str, Optional[int]]],
    /,
    *,
    start: Any = None,
    smooth: Optional[int] = None,
    aspect: float = _DEFAULT_ASPECT,
) -> Overlay:
    plots = (
        plot_new_cases(
            country, scale=scale, start=start, smooth=smooth, aspect=aspect
        )
        for country, scale in countries_and_scales
    )
    return reduce(add, plots).cols(1)
