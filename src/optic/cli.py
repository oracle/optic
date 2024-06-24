import click

from optic.cluster.cluster_service import (
    get_cluster_list,
    package_cluster_info,
    print_cluster_info,
)
from optic.index.index_info import get_index_info
from optic.common.exceptions import OpticError


@click.group(help="optic: Opensearch Tools for Indices and Cluster")
def cli():
    pass


@cli.command()
@click.option(
    "--config-path",
    default="~/.optic/optic-config.json",
    help="specify a non-default configuration file path"
    "(default is ~/.optic/optic-config.json",
)
@click.option(
    "--byte-type",
    default="gb",
    type=click.Choice(["mb", "gb"], case_sensitive=False),
    help="specify the mb or gb type for storage calculation (default is gb)",
)
def cluster_info(config_path, byte_type):
    """Prints status of all clusters in configuration file"""
    try:
        print_cluster_info(
            package_cluster_info(get_cluster_list(config_path, byte_type))
        )
    except OpticError as e:
        print(e)
        exit(1)


@cli.command()
@click.option("--name", required=True, help="Index name")
def index_info(name):
    """Get Index information"""
    print(get_index_info(name))


if __name__ == "__main__":
    cli()
