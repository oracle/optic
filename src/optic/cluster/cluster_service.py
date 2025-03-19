# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

from terminaltables import AsciiTable

from optic.common.optic_color import OpticColor


def get_cluster_info(config_info) -> list:
    """
    Retrieves and packages Cluster information into a list of dictionaries

    :param ClusterConfig config_info: Cluster Configuration info object
    :return: list of dictionaries containing cluster information
    :rtype: list
    """
    cluster_info = []
    for cluster in config_info.selected_cluster_objects:
        usage = cluster.storage_percent
        status = cluster.health.status
        cluster_info.append(
            {"name": cluster.custom_name, "status": status, "usage": usage}
        )
    return cluster_info


def print_cluster_info(cluster_info, no_color, storage_percent_thresholds) -> None:
    """
    Prints cluster information

    :param list cluster_info: list of dictionaries containing cluster information
    :param bool no_color: disable colored output if value is true
    :param dict storage_percent_thresholds: dict of storage percent thresholds
    :return: None
    :rtype: None
    """
    table = build_cluster_info_table(cluster_info, no_color, storage_percent_thresholds)

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
