# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

from terminaltables import AsciiTable

from optic.cluster.cluster import Cluster
from optic.common.exceptions import OpticConfigurationFileError
from optic.common.optic_color import OpticColor


def get_selected_clusters(cluster_config, selected_cluster_names):
    """
    Given the optic cluster configuration and a list of cluster names,
    return a list of Cluster type objects

    :param ClusterConfig cluster_config: Cluster Configuration info object
    :param list selected_cluster_names: list of cluster or cluster group names
    :return: List of Cluster type objects
    :rtype: list[Cluster]
    """
    selected_clusters = []

    # Replaces cluster group names with associated clusters
    if cluster_config.groups:
        for group_name, group_clusters in cluster_config.groups.items():
            if group_name in selected_cluster_names:
                selected_cluster_names.extend(group_clusters)
                selected_cluster_names.remove(group_name)

    # Delete repeats
    selected_cluster_names = list(set(selected_cluster_names))

    # If no clusters are specified, use all clusters in the ClusterConfig
    default_behavior = len(selected_cluster_names) == 0

    # If a cluster name is in selected_clusters list, create a Cluster object to represent it
    for cluster_name, cluster_data in cluster_config.clusters.items():
        if (cluster_name in selected_cluster_names) or default_behavior:
            do_ssl = cluster_data.get("verify_ssl", True)
            if type(do_ssl) is not bool:
                raise OpticConfigurationFileError(
                    "Unrecognized SSL option for " + cluster_name
                )
            cluster = Cluster(
                url=cluster_data["url"],
                auth={
                    "username": cluster_data["username"],
                    "password": cluster_data["password"],
                },
                verify_ssl=do_ssl,
                name=cluster_name,
            )

            selected_clusters.append(cluster)
            if selected_cluster_names:
                selected_cluster_names.remove(cluster_name)

    # Notifies if any non-existent clusters provided
    for missing_cluster in selected_cluster_names:
        print(missing_cluster, "is not present in cluster configuration file")
    return selected_clusters


def get_cluster_info(clusters) -> list:
    """
    Retrieves and packages Cluster information into a list of dictionaries

    :param list clusters: list of Cluster type objects
    :return: list of dictionaries containing cluster information
    :rtype: list
    """
    cluster_info = []
    for cluster in clusters:
        usage = cluster.storage_percent
        status = cluster.health.status
        cluster_info.append({"name": cluster.name, "status": status, "usage": usage})
    return cluster_info


def print_cluster_info(cluster_info, optic_settings) -> None:
    """
    Prints cluster information

    :param list cluster_info: list of dictionaries containing cluster information
    :param bool no_color: disable colored output if value is true
    :param dict storage_percent_thresholds: dict of storage percent thresholds
    :return: None
    :rtype: None
    """
    table = build_cluster_info_table(
        cluster_info,
        optic_settings["no_color"],
        optic_settings["storage_percent_thresholds"],
    )

    # only display the table if at least one valid cluster was found
    if table:
        print(table.table)
    else:
        print("Unable to display cluster information. No valid clusters were selected.")


def build_cluster_info_table(
    cluster_info, no_color, storage_percent_thresholds
) -> AsciiTable:
    """
    Creates an AsciiTable object populated with cluster information

    :param list cluster_info: list of dictionaries containing cluster information
    :param bool no_color: disable colored output if value is true
    :param dict storage_percent_thresholds: dict of storage percent thresholds
    :return: formatted table of cluster information
    :rtype: AsciiTable
    """

    if not cluster_info:
        return None

    optic_color = OpticColor()
    if no_color:
        optic_color.disable_colors()

    print_data = [["Cluster", "Status", "Storage Use (%)"]]
    for stats in cluster_info:
        status = stats["status"]
        match status:
            case "red":
                status = optic_color.RED + status + optic_color.STOP
            case "yellow":
                status = optic_color.YELLOW + status + optic_color.STOP
            case "green":
                status = optic_color.GREEN + status + optic_color.STOP

        usage = stats["usage"]
        if usage < storage_percent_thresholds["GREEN"]:
            usage = optic_color.GREEN + str(usage) + optic_color.STOP
        elif usage < storage_percent_thresholds["YELLOW"]:
            usage = optic_color.YELLOW + str(usage) + optic_color.STOP
        elif usage <= storage_percent_thresholds["RED"]:
            usage = optic_color.RED + str(usage) + optic_color.STOP

        print_data.append([stats["name"], status, usage])

    table = AsciiTable(print_data)
    table.title = "Cluster Info"
    return table
