# ** OPTIC version 1.0.0
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

from terminaltables import AsciiTable

from optic.common.opticolor import Opticolor


def get_cluster_info(cluster_list) -> list:
    """
    Retrieves and packages Cluster information into a list of dictionaries

    :param list cluster_list: list of Cluster objects
    :return: list of dictionaries containing cluster information
    :rtype: list
    """
    clusters_dicts = []
    for cluster in cluster_list:
        usage = cluster.storage_percent
        status = cluster.health.status
        clusters_dicts.append(
            {"name": cluster.custom_name, "status": status, "usage": usage}
        )
    return clusters_dicts


def print_cluster_info(cluster_dicts, no_color) -> None:
    """
    Prints Cluster Information

    :param list cluster_dicts: list of dictionaries of cluster information
    :param bool no_color: whether colored output or not
    :return: None
    :rtype: None
    """
    opticolor = Opticolor()
    if no_color:
        opticolor.disable_colors()

    print_data = [["ENV", "STATUS", "STORAGE USE (%)"]]
    for stats in cluster_dicts:
        status = stats["status"]
        match status:
            case "red":
                status = opticolor.RED + status + opticolor.STOP
            case "yellow":
                status = opticolor.YELLOW + status + opticolor.STOP
            case "green":
                status = opticolor.GREEN + status + opticolor.STOP

        print_data.append([stats["name"], status, stats["usage"]])

    table = AsciiTable(print_data)
    table.title = "Cluster Info"
    print(table.table)
