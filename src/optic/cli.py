# ** OPTIC
# **
# ** Copyright (c) 2024-2025 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

import click
from click import Option

from optic.alias.alias_service import get_alias_info, print_alias_info
from optic.cluster.cluster import configure_cluster
from optic.cluster.cluster_service import (
    get_cluster_info,
    get_selected_clusters,
    print_cluster_info,
)
from optic.common.config import OpticSettings, read_cluster_config, yaml_load
from optic.common.exceptions import OpticConfigurationFileError, OpticError
from optic.index.index_service import get_index_info, print_index_info
from optic.initialize.initialize_service import initialize_optic


def read_optic_settings(ctx):
    try:
        ctx.obj["optic_settings"].update(
            OpticSettings(
                yaml_load(ctx.obj["optic_settings"]["optic_settings_file_path"])
            ).fields
        )
    except OpticConfigurationFileError as e:
        print(e)
        exit(1)
    return ctx.obj["optic_settings"]


def read_cluster_configuration(cluster_config_file_path):
    try:
        cluster_config = read_cluster_config(cluster_config_file_path)
    except OpticConfigurationFileError as e:
        print(e)
        exit(1)

    return cluster_config


def get_default_from_optic_settings(setting_name) -> type[Option] | None:
    """
    Constructs custom class to support default values for cli options
    :param string setting_name: name of the setting that drives default option value
    :return: class with get_default method
    :rtype: type[Option] | None
    """

    class OptionDefaultFromOpticSettings(click.Option):
        def get_default(self, ctx, call=True):
            try:
                if not ctx.obj:
                    # Dummy so shell completion works before setting Settings context
                    self.default = None
                else:
                    self.default = ctx.obj["optic_settings"][setting_name]
            except KeyError:
                print(
                    f"[{setting_name}] attribute not found in optic settings file "
                    f'[{ctx.obj["optic_settings"]["optic_settings_file_path"]}]'
                )
                exit(1)
            return super(OptionDefaultFromOpticSettings, self).get_default(ctx)

    return OptionDefaultFromOpticSettings


# BEGIN: OPTIC Entry Point
@click.group(help="optic: OpenSearch Tools for Indices and Cluster")
@click.option(
    "--settings",
    "optic_settings_file_path",
    default="~/.optic/optic-settings.yaml",
    help="specify a non-default optic settings file",
    show_default=True,
)
@click.pass_context
def cli(ctx, optic_settings_file_path):
    ctx.obj = {"optic_settings": {"optic_settings_file_path": optic_settings_file_path}}
    ctx.ensure_object(dict)


# END: OPTIC Entry Point


# BEGIN: initialize command (No tool domain)
@cli.command()
@click.option(
    "--cluster-config",
    "cluster_config_file_path",
    default="~/.optic/cluster-config.yaml",
    help="specify a non-default cluster configuration file",
    show_default=True,
)
@click.pass_context
def init(ctx, cluster_config_file_path):
    """Initialize OPTIC settings,  configuration, and shell completion"""

    optic_settings = ctx.obj["optic_settings"]
    try:
        initialize_optic(
            optic_settings["optic_settings_file_path"], cluster_config_file_path
        )
    except OpticError as e:
        print(e)
        exit(1)


# END: initialize command (No tool domain)


# BEGIN: Cluster Tool Domain
@cli.group(help="cluster: actions related to OpenSearch clusters")
@click.pass_context
def cluster(ctx):
    read_optic_settings(ctx)
    ctx.ensure_object(dict)


# BEGIN: Info Tool
@cluster.command()
@click.option(
    "--cluster-config",
    "cluster_config_file_path",
    cls=get_default_from_optic_settings("cluster_config_file_path"),
    help="specify a non-default cluster configuration file",
    show_default=True,
)
@click.option(
    "-c",
    "--cluster",
    "cluster_selection",
    multiple=True,
    default=(),
    help="filter results to specific cluster(s) and/or group(s). "
    "Argument can be used multiple times. ",
)
@click.option(
    "--no-color",
    is_flag=True,
    cls=get_default_from_optic_settings("disable_terminal_color"),
    help="disable terminal color output",
    show_default=True,
)
@click.pass_context
def info(ctx, cluster_config_file_path, cluster_selection, no_color):

    optic_settings = ctx.obj["optic_settings"]
    optic_settings["no_color"] = no_color
    cluster_config = read_cluster_configuration(cluster_config_file_path)

    """Prints status of all clusters in configuration file"""
    try:
        selected_clusters = get_selected_clusters(
            cluster_config, list(cluster_selection)
        )
        cluster_info = get_cluster_info(selected_clusters)
        print_cluster_info(cluster_info, optic_settings)
    except OpticError as e:
        print(e)
        exit(1)


# END: Info Tool
# END: Cluster Tool Domain


# BEGIN: Index Tool Domain
@cli.group(help="actions related to OpenSearch indices")
@click.pass_context
def index(ctx):
    read_optic_settings(ctx)
    ctx.ensure_object(dict)


# BEGIN: Info Tool
@index.command()
@click.option(
    "--cluster-config",
    "cluster_config_file_path",
    cls=get_default_from_optic_settings("cluster_config_file_path"),
    help="specify a non-default cluster configuration file",
    show_default=True,
)
@click.option(
    "-c",
    "--cluster",
    "cluster_selection",
    multiple=True,
    default=(),
    help="filter results to specific cluster(s) and/or group(s). "
    "Argument can be used multiple times. ",
)
@click.option(
    "-p",
    "--search-pattern",
    cls=get_default_from_optic_settings("search_pattern"),
    help="specify a glob search pattern for indices",
    show_default=True,
)
@click.option(
    "--no-color",
    is_flag=True,
    cls=get_default_from_optic_settings("disable_terminal_color"),
    help="disable terminal color output",
    show_default=True,
)
@click.option(
    "-w",
    "--write-alias-only",
    is_flag=True,
    default=None,
    help="filter to only display indices that are targets of write aliases",
)
@click.option("--min-age", type=int, help="minimum age of index")
@click.option("--max-age", type=int, help="maximum age of index")
@click.option(
    "--min-index-size",
    help="filter by minimum size of index (accepts kb, mb, gb, tb) Example: 1mb",
)
@click.option(
    "--max-index-size",
    help="filter by maximum size of index (accepts kb, mb, gb, tb) Example: 10gb",
)
@click.option(
    "--min-shard-size",
    help="filter by minimum average size of index primary shards "
    "(accepts kb, mb, gb, tb) Example: 1mb",
)
@click.option(
    "--max-shard-size",
    help="filter by maximum average size of index primary shards "
    "(accepts kb, mb, gb, tb) Example: 10gb",
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
    "Supports multiple exclusions Example: -t ISM -t SYSTEM",
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
@click.pass_context
def info(
    ctx,
    cluster_config_file_path,
    cluster_selection,
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
    no_color,
):

    # the initial settings and defaults are read from the optic settings file
    # they are then overridden with any command line arguments that are passed

    optic_settings = ctx.obj["optic_settings"]
    optic_settings["no_color"] = no_color
    optic_settings["search_pattern"] = search_pattern
    cluster_config = read_cluster_configuration(cluster_config_file_path)

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
        selected_clusters = get_selected_clusters(
            cluster_config, list(cluster_selection)
        )

        for cluster in selected_clusters:
            configure_cluster(cluster, optic_settings)

        index_info = get_index_info(selected_clusters, filters, sort_by)
        print_index_info(index_info, optic_settings)
    except OpticError as e:
        print(e)
        exit(1)


# END: Info Tool
# END: Index Tool Domain


# BEGIN: Alias Tool Domain
@cli.group(help="alias: actions related to OpenSearch aliases")
@click.pass_context
def alias(ctx):
    read_optic_settings(ctx)
    ctx.ensure_object(dict)


# BEGIN: Info Tool
@alias.command()
@click.option(
    "--cluster-config",
    "cluster_config_file_path",
    cls=get_default_from_optic_settings("cluster_config_file_path"),
    help="specify a non-default cluster configuration file",
    show_default=True,
)
@click.option(
    "-c",
    "--cluster",
    "cluster_selection",
    multiple=True,
    default=(),
    help="filter results to specific cluster(s) and/or group(s). "
    "Argument can be used multiple times. ",
)
@click.option(
    "-p",
    "--search-pattern",
    cls=get_default_from_optic_settings("search_pattern"),
    help="specify a glob search pattern for indices",
    show_default=True,
)
@click.option(
    "--no-color",
    is_flag=True,
    cls=get_default_from_optic_settings("disable_terminal_color"),
    help="disable terminal color output",
    show_default=True,
)
@click.pass_context
def info(ctx, cluster_config_file_path, cluster_selection, search_pattern, no_color):
    """Prints information about aliases in use"""

    optic_settings = ctx.obj["optic_settings"]
    optic_settings["no_color"] = no_color
    optic_settings["search_pattern"] = search_pattern
    cluster_config = read_cluster_configuration(cluster_config_file_path)

    try:
        cluster_config = read_cluster_config(cluster_config_file_path)
        selected_clusters = get_selected_clusters(
            cluster_config, list(cluster_selection)
        )

        for cluster in selected_clusters:
            configure_cluster(cluster, optic_settings)

        alias_info = get_alias_info(selected_clusters)
        print_alias_info(alias_info, no_color)
    except OpticError as e:
        print(e)
        exit(1)


# END: Info Tool
# END: Alias Tool Domain
