import click

from optic.cluster.cluster_info import get_cluster_info
from optic.index.index_info import get_index_info


@click.group(help="optic: Opensearch Tools for Indices and Cluster")
def cli():
    pass


@cli.command()
@click.option("--name", required=True, help="Cluster name")
def cluster_info(name):
    """Get Cluster information"""
    print(get_cluster_info(name))


@cli.command()
@click.option("--name", required=True, help="Index name")
def index_info(name):
    """Get Index information"""
    print(get_index_info(name))


if __name__ == "__main__":
    cli()
