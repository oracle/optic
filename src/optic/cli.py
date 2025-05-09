# ** OPTIC
# **
# ** Copyright (c) 2024-2025 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

import click
from click import Option

from optic.alias.alias_service import get_alias_info, print_alias_info
from optic.cluster.cluster_service import get_cluster_info, print_cluster_info
from optic.common.config import ClusterConfig, Settings, yaml_load
from optic.common.exceptions import OpticError
from optic.index.index_service import get_index_info, print_index_info
from optic.initialize.initialize_service import initialize_optic


def default_from_settings(setting_name) -> type[Option] | None:
    """
    Constructs custom class to define some Click Option behaviors
    :param string setting_name: name of the setting needed for Click option default
    :return: class to override some Click Option behaviors
    :rtype: type[Option] | None
    """

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


# BEGIN: OPTIC Entry Point
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


# END: OPTIC Entry Point


# BEGIN: initialize command (No tool domain)
@cli.command()
def init():
    """Initialize OPTIC settings,  configuration, and shell completion"""
    try:
        initialize_optic()
    except OpticError as e:
        print(e)
        exit(1)


# END: initialize command (No tool domain)


# BEGIN: Cluster Tool Domain
@cli.group(help="cluster: Tool domain containing tools related to OpenSearch clusters")
@click.pass_context
def cluster(ctx):
    ctx.ensure_object(dict)
    try:
        settings = Settings(yaml_load(ctx.obj["settings_file_path"]))
        ctx.obj = settings.fields
    except OpticError as e:
        print(e)
        exit(1)


# BEGIN: Info Tool
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
@click.option(
    "--no-color",
    is_flag=True,
    cls=default_from_settings("disable_terminal_color"),
    help="disable terminal color output (default is disable_terminal_color"
    " in settings yaml file)",
)
@click.option(
    "--storage-percent-thresholds",
    type=dict,
    cls=default_from_settings("storage_percent_thresholds"),
    help="specify thresholds for storage % coloring.  "
    "**THIS SHOULD BE DONE UNDER THE storage_percent_thresholds "
    "FIELD IN THE SETTINGS YAML FILE, NOT ON CL**",
)
@click.pass_context
def info(
    ctx, clusters, cluster_config, byte_type, no_color, storage_percent_thresholds
):
    """Prints status of all clusters in configuration file"""
    try:
        desired_clusters = list(clusters)
        desired_cluster_properties = {"byte_type": byte_type}
        config_info = ClusterConfig(
            yaml_load(cluster_config), desired_clusters, desired_cluster_properties
        )
        cluster_info_list = get_cluster_info(config_info)
        print_cluster_info(cluster_info_list, no_color, storage_percent_thresholds)
    except OpticError as e:
        print(e)
        exit(1)


# END: Info Tool
# END: Cluster Tool Domain


# BEGIN: Index Tool Domain
@cli.group(help="index: Tool domain containing tools related to OpenSearch indices")
@click.pass_context
def index(ctx):
    ctx.ensure_object(dict)
    try:
        settings = Settings(yaml_load(ctx.obj["settings_file_path"]))
        ctx.obj = settings.fields
    except OpticError as e:
        print(e)
        exit(1)


# BEGIN: Info Tool
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
    cls=default_from_settings("default_search_pattern"),
    help="specify a glob search pattern for indices (default is"
    " default_search_pattern field in settings yaml file)",
)
@click.option(
    "-w",
    "--write-alias-only",
    is_flag=True,
    default=None,
    help="filter to only display indices that are targets of write aliases",
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
            "write-alias",
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
@click.option(
    "--no-color",
    is_flag=True,
    cls=default_from_settings("disable_terminal_color"),
    help="disable terminal color output (default is disable_terminal_color"
    " in settings yaml file)",
)
@click.pass_context
def info(
    ctx,
    cluster_config,
    clusters,
    search_pattern,
    write_alias_only,
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
    no_color,
):
    """Get Index information"""
    try:
        filters = {
            "write_alias_only": write_alias_only,
            "min_age": min_age,
            "max_age": max_age,
            "min_index_size": min_index_size,
            "max_index_size": max_index_size,
            "min_shard_size": min_shard_size,
            "max_shard_size": max_shard_size,
            "min_doc_count": min_doc_count,
            "max_doc_count": max_doc_count,
            "type_filter": list(type_filter),
        }
        sort_by = list(sort_by)
        desired_clusters = list(clusters)
        desired_cluster_properties = {
            "index_search_pattern": search_pattern,
            "index_types_dict": index_types,
        }
        config_info = ClusterConfig(
            yaml_load(cluster_config), desired_clusters, desired_cluster_properties
        )
        index_info_dict = get_index_info(config_info, filters, sort_by)
        print_index_info(index_info_dict, no_color)
    except OpticError as e:
        print(e)
        exit(1)


# END: Info Tool
# END: Index Tool Domain


# BEGIN: Alias Tool Domain
@cli.group(help="alias: Tool domain containing tools related to OpenSearch aliases")
@click.pass_context
def alias(ctx):
    ctx.ensure_object(dict)
    try:
        settings = Settings(yaml_load(ctx.obj["settings_file_path"]))
        ctx.obj = settings.fields
    except OpticError as e:
        print(e)
        exit(1)


# BEGIN: Info Tool
@alias.command()
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
    "-p",
    "--search-pattern",
    cls=default_from_settings("default_search_pattern"),
    help="specify a glob search pattern for aliases (default is"
    " default_search_pattern field in settings yaml file)",
)
@click.option(
    "--no-color",
    is_flag=True,
    cls=default_from_settings("disable_terminal_color"),
    help="disable terminal color output (default is disable_terminal_color"
    " in settings yaml file)",
)
@click.pass_context
def info(ctx, clusters, cluster_config, search_pattern, no_color):
    """Prints information about aliases in use"""
    try:
        desired_clusters = list(clusters)
        desired_cluster_properties = {
            "index_search_pattern": search_pattern,
        }
        config_info = ClusterConfig(
            yaml_load(cluster_config), desired_clusters, desired_cluster_properties
        )
        alias_info_list = get_alias_info(config_info)
        print_alias_info(alias_info_list, no_color)
    except OpticError as e:
        print(e)
        exit(1)


# END: Info Tool
# END: Alias Tool Domain
