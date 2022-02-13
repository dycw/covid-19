from os import environ
from os import getenv
from pathlib import Path
from typing import cast

import holoviews.plotting.bokeh  # type: ignore # noqa: F401
from click import DateTime
from click import command
from click import option
from holoviews import save

from covid_19.covid_19 import get_combined_plot


@command()
@option(
    "-s", "--start", type=DateTime(), default="2021-12-01", show_default=True
)
@option("--smooth", type=int, default=3, show_default=True)
def main(start: str, smooth: int) -> None:
    countries_and_scales = [("HKG", None), ("JPN", 3), ("USA", 3), ("GBR", 3)]
    plot = get_combined_plot(countries_and_scales, start=start, smooth=smooth)
    current = cast(str, getenv("PATH"))
    bin_ = Path.cwd().joinpath("bin").as_posix()
    environ["PATH"] = ":".join([current, bin_])
    save(plot, Path("assets", "plot.png"))


if __name__ == "__main__":
    main()
