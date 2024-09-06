"""This is a simple CLI that demonstrates hot to use the library.

Typical usage example:
$ python -m data_access example
Running example command.
"""

import click


@click.group(name="cli")
def cli() -> None:
    """Click command group for the library."""


@cli.command(name="example")
def example() -> None:
    """Example of how to use the data-access library.

    This is primarily intended for developer use.
    """
    print("Running example command.")


if __name__ == "__main__":
    cli()
