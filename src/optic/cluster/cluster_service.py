# ** OPTIC version 1.0.
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

from terminaltables import AsciiTable


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


def print_cluster_info(cluster_dicts) -> None:
    """
    Prints Cluster Information

    :param list cluster_dicts: list of dictionaries of cluster information
    :return: None
    :rtype: None
    """
    print_data = [["ENV", "STATUS", "STORAGE USE (%)"]]
    for stats in cluster_dicts:
        print_data.append([stats["name"], stats["status"], stats["usage"]])

    table = AsciiTable(print_data)
    table.title = "Cluster Info"
    print(table.table)
