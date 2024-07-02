import click

from optic.cluster.cluster_service import (
    get_cluster_info,
    get_cluster_list,
    print_cluster_info,
)
from optic.common.config import Settings
from optic.common.exceptions import OpticError
from optic.index.index_service import (
    filter_and_sort_indices,
    get_clusters_and_groups,
    get_index_info,
    print_index_info,
)


def default_from_settings(setting_name):
    class OptionDefaultFromSettings(click.Option):
        def get_default(self, ctx, call=True):
            try:
                self.default = ctx.obj[setting_name]
            except KeyError:
                print(setting_name, "not found in specified settings file")
                exit(1)
            return super(OptionDefaultFromSettings, self).get_default(ctx)

    return OptionDefaultFromSettings


@click.group(help="optic: Opensearch Tools for Indices and Cluster")
@click.option(
    "--settings",
    default="~/.optic/optic-settings.yaml",
    help="specify a non-default settings file path "
    "(default is ~/.optic/optic-settings.yaml",
)
@click.pass_context
def cli(ctx, settings):
    ctx.ensure_object(dict)
    try:
        settings = Settings(settings)
        ctx.obj = settings.fields
    except OpticError as e:
        print(e)
        exit(1)


@cli.command()
@click.option(
    "--cluster-config",
    cls=default_from_settings("default_cluster_config_file_path"),
    help="specify a non-default configuration file path "
    "(default is default_cluster_config_file_path field in settings yaml file",
)
@click.option(
    "--byte-type",
    cls=default_from_settings("default_cluster_info_byte_type"),
    type=click.Choice(["mb", "gb"], case_sensitive=False),
    help="specify the mb or gb type for storage calculation "
    "(default is default_cluster_info_byte_type in settings yaml file)",
)
@click.pass_context
def cluster_info(ctx, cluster_config, byte_type):
    """Prints status of all clusters in configuration file"""
    try:
        cluster_list = get_cluster_list(cluster_config, byte_type)
        cluster_info_dict = get_cluster_info(cluster_list)
        print_cluster_info(cluster_info_dict)
    except OpticError as e:
        print(e)
        exit(1)


@cli.command()
@click.option(
    "-c",
    "--clusters",
    multiple=True,
    default=(),
    help="Specify cluster groups and/or specific clusters to query. "
    "Default behavior queries all clusters present in config file. "
    "(Entries must be present in config file) Eg: -c my_cluster_group_1"
    " -c my_cluster_group_2 -c my_cluster_group_4 -c my_cluster",
)
@click.option(
    "-p",
    "--search-pattern",
    cls=default_from_settings("default_index_search_pattern"),
    help="specify a search pattern for indices (default is"
    " default_index_search_pattern field in settings yaml file)",
)
@click.option(
    "--cluster-config",
    cls=default_from_settings("default_cluster_config_file_path"),
    help="specify a non-default configuration file path "
    "(default is default_cluster_config_file_path field in settings yaml file)",
)
@click.option("--min-age", help="minimum age of index")
@click.option("--max-age", help="maximum age of index")
@click.option(
    "--min-index-size",
    help="filter by minimum size of index (accepts kb, mb, gb, tb) Eg: 1mb",
)
@click.option(
    "--max-index-size",
    help="filter by maximum size of index (accepts kb, mb, gb, tb) Eg: 10gb",
)
@click.option(
    "--min-shard-size",
    help="filter by minimum average size of index primary shards "
    "(accepts kb, mb, gb, tb) Eg: 1mb",
)
@click.option(
    "--max-shard-size",
    help="filter by maximum average size of index primary shards "
    "(accepts kb, mb, gb, tb) Eg: 10gb",
)
@click.option("--min-doc-count", help="filter by minimum number of documents")
@click.option("--max-doc-count", help="filter by maximum number of documents")
@click.option(
    "-t",
    "--type-filter",
    multiple=True,
    default=(),
    type=str,
    help="specify the index types to exclude.  "
    "Supports multiple exclusions Eg: -t ISM -t SYSTEM",
)
@click.option(
    "-s",
    "--sort-by",
    multiple=True,
    default=(),
    type=click.Choice(
        [
            "age",
            "name",
            "index-size",
            "shard-size",
            "doc-count",
            "type",
            "primary-shards",
            "replica-shards",
        ],
        case_sensitive=False,
    ),
    help="Specify field(s) to sort by",
)
@click.option(
    "--index-types",
    type=dict,
    cls=default_from_settings("default_index_type_patterns"),
    help="specify regular expression search pattern for index types.  "
    "**THIS SHOULD BE DONE UNDER THE default_index_type_patterns "
    "FIELD IN THE SETTINGS YAML FILE, NOT ON CL**",
)
@click.pass_context
def index_info(
    ctx,
    cluster_config,
    clusters,
    search_pattern,
    min_age,
    max_age,
    min_index_size,
    max_index_size,
    min_shard_size,
    max_shard_size,
    min_doc_count,
    max_doc_count,
    type_filter,
    sort_by,
    index_types,
):
    """Get Index information"""
    try:
        filters = {
            "min_age": min_age,
            "max_age": max_age,
            "min_index_size": min_index_size,
            "max_index_size": max_index_size,
            "min_shard_size": min_shard_size,
            "max_shard_size": max_shard_size,
            "min_doc_count": min_doc_count,
            "max_doc_count": max_doc_count,
            "type_filter": type_filter,
        }
        cluster_list = get_clusters_and_groups(
            cluster_config, clusters, search_pattern, index_types
        )
        index_list = filter_and_sort_indices(cluster_list, filters, sort_by)
        index_info_dict = get_index_info(index_list)
        print_index_info(index_info_dict)
    except OpticError as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    cli(obj={})
