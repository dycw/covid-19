from os import environ
from os import getenv
from pathlib import Path
from typing import cast

import holoviews.plotting.bokeh  # type: ignore # noqa: F401
from holoviews import save

from covid_19.covid_19 import get_combined_plot


def main() -> None:
    countries_and_scales = [("HKG", None), ("JPN", 3), ("USA", 3), ("GBR", 3)]
    plot = get_combined_plot(countries_and_scales, start="2021-12-01", smooth=3)
    current = cast(str, getenv("PATH"))
    bin_ = Path.cwd().joinpath("bin").as_posix()
    environ["PATH"] = ":".join([current, bin_])
    save(plot, "plot.png")


if __name__ == "__main__":
    main()
