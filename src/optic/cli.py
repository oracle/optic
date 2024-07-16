import click

from optic.cluster.cluster_service import get_cluster_info, print_cluster_info
from optic.common.config import ClusterConfig, Settings, yaml_load
from optic.common.exceptions import OpticError
from optic.common.initialize import initialize_optic
from optic.index.index_service import (
    filter_and_sort_indices,
    get_index_info,
    print_index_info,
)


def default_from_settings(setting_name):
    class OptionDefaultFromSettings(click.Option):
        def get_default(self, ctx, call=True):
            try:
                if not ctx.obj:
                    # Dummy so shell completion works before setting Settings context
                    self.default = None
                else:
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
    ctx.obj["settings_file_path"] = settings


@cli.command()
@click.option(
    "--cluster-config-setup",
    prompt="Would you like to create a cluster configuration  "
    "file at ~/.optic/cluster-config.yaml?",
    type=click.Choice(["y", "N"], case_sensitive=False),
    help="Prompts user for permission to create cluster config file",
)
@click.option(
    "--settings-setup",
    prompt="Would you like to set up a settings file at ~/.optic/optic-settings.yaml?",
    type=click.Choice(["y", "N"], case_sensitive=False),
    help="Prompts user for permission to create cluster config file",
)
@click.option(
    "--shell-setup",
    prompt="Would you like to set up shell completion?  NOTE: This will involve  "
    "creating a file in ~/.optic directory and appending a command to source it  "
    "to your shell configuration file",
    type=click.Choice(["y", "N"], case_sensitive=False),
    help="Prompts user for permission to setup shell completion",
)
def init(cluster_config_setup, settings_setup, shell_setup):
    """Initialize OPTIC settings,  configuration, and shell completion"""
    try:
        config_bool = cluster_config_setup.lower() == "y"
        settings_bool = settings_setup.lower() == "y"
        shell_bool = shell_setup.lower() == "y"
        initialize_optic(config_bool, settings_bool, shell_bool)
    except OpticError as e:
        print(e)
        exit(1)


@cli.group(help="cluster: Utilities relating to clusters")
@click.pass_context
def cluster(ctx):
    ctx.ensure_object(dict)
    try:
        settings = Settings(yaml_load(ctx.obj["settings_file_path"]))
        ctx.obj = settings.fields
    except OpticError as e:
        print(e)
        exit(1)


@cluster.command()
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
def info(ctx, clusters, cluster_config, byte_type):
    """Prints status of all clusters in configuration file"""
    try:
        desired_clusters = list(clusters)
        desired_cluster_properties = {"byte_type": byte_type}
        config_info = ClusterConfig(
            yaml_load(cluster_config), desired_clusters, desired_cluster_properties
        )
        cluster_info_dict = get_cluster_info(config_info.desired_cluster_objects)
        print_cluster_info(cluster_info_dict)
    except OpticError as e:
        print(e)
        exit(1)


@cli.group(help="index: Utilities relating to indices")
@click.pass_context
def index(ctx):
    ctx.ensure_object(dict)
    try:
        settings = Settings(yaml_load(ctx.obj["settings_file_path"]))
        ctx.obj = settings.fields
    except OpticError as e:
        print(e)
        exit(1)


@index.command()
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
@click.option("--min-age", type=int, help="minimum age of index")
@click.option("--max-age", type=int, help="maximum age of index")
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
@click.option("--min-doc-count", type=int, help="filter by minimum number of documents")
@click.option("--max-doc-count", type=int, help="filter by maximum number of documents")
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
def info(
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
        desired_clusters = list(clusters)
        desired_cluster_properties = {
            "index_search_pattern": search_pattern,
            "index_types_dict": index_types,
        }
        config_info = ClusterConfig(
            yaml_load(cluster_config), desired_clusters, desired_cluster_properties
        )
        index_list = filter_and_sort_indices(
            config_info.desired_cluster_objects, filters, sort_by
        )
        index_info_dict = get_index_info(index_list)
        print_index_info(index_info_dict)
    except OpticError as e:
        print(e)
        exit(1)
