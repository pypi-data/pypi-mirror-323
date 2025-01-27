import typer
from zoneinfo import available_timezones
from typing import Optional
from typing_extensions import Annotated
from teamzones.time_format import format_time
from teamzones.inputs import *

app = typer.Typer(no_args_is_help=True)


@app.command()
def at(
    timezones: Annotated[
        str,
        typer.Argument(
            help="CSV separated list of time zones to present times for; use list-countries to get supported values"
        ),
    ],
    time: Annotated[
        Optional[str], typer.Argument(help="Any input accepted by dateutil.parser")
    ] = None,
    time_format: Annotated[
        str,
        typer.Option(help="Format string accepted by datetime.strftime"),
    ] = None,
    separator: Annotated[str, typer.Option(help="Output separator")] = " / ",
):
    """
    Given a set of timezones and a time, provide local times at the given timezones
    """
    zone_infos = timezones_csv_to_zone_info_list(timezones)
    given_time = time_input_to_datetime(time)
    zoned_times = list(map((lambda zi: given_time.astimezone(zi)), zone_infos))
    formatted_times = list(map((lambda t: format_time(t, time_format)), zoned_times))
    typer.echo(separator.join(formatted_times))


@app.command()
def list_timezones():
    """
    List available timezones
    """
    timezones = sorted(available_timezones())
    for timezone in timezones:
        print(timezone)


if __name__ == "__main__":
    app()
