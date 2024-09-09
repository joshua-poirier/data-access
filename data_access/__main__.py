"""This is a simple CLI that demonstrates hot to use the library.

Typical usage example:
$ python -m data_access example
Running example command.
"""

import click
import pandas as pd

from data_access.sources.google_drive import GoogleDriveClient


@click.group(name="cli")
def cli() -> None:
    """Click command group for the library."""


@cli.command(name="example")
def example() -> None:
    """Example of how to use the data-access library.

    This is primarily intended for developer use.
    """
    client = GoogleDriveClient(io_options={"encoding": "utf-8", "header": 0})
    client.get_file_id(filename="PRAProductCodes.csv")

    # stream data into dataframe
    df: pd.DataFrame = client.read()
    print(df.head())


if __name__ == "__main__":
    cli()
