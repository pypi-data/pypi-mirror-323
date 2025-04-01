"""Console script for meboot."""

import click


@click.command()
def main():
    """Main entrypoint."""
    click.echo("maxentboot")
    click.echo("=" * len("maxentboot"))
    click.echo("Maximum Entropy Bootstrap for timeseries")


if __name__ == "__main__":
    main()  # pragma: no cover
