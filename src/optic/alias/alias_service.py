# ** OPTIC version 1.0.0
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

from terminaltables import AsciiTable

from optic.common.opticolor import Opticolor


def get_alias_info(alias_list) -> list:
    """
    Retrieves and packages Alias information into a list of dictionaries

    :param list alias_list: list of Alias objects
    :return: list of dictionaries containing alias information
    :rtype: list
    """
    alias_dicts = []
    for alias in alias_list:
        target_list = []
        for target in alias.targets:
            target_list.append(
                {
                    "cluster_name": alias.cluster_name,
                    "index_name": target.index,
                    "filter": target.filter,
                    "routing_index": getattr(target, "routing.index"),
                    "routing_search": getattr(target, "routing.search"),
                    "write_target": target.is_write_index,
                }
            )
        alias_dicts.append({alias.alias_name: target_list})
    return alias_dicts


def print_alias_info(alias_dicts, no_color) -> None:
    """
    Prints Alias Information

    :param list alias_dicts: list of dictionaries of alias information
    :param bool no_color: whether colored output or not
    :return: None
    :rtype: None
    """
    opticolor = Opticolor()
    if no_color:
        opticolor.disable_colors()

    for alias in alias_dicts:
        print_data = [
            [
                "Target Index",
                "Write Target",
                "Filter",
                "Routing Index",
                "Routing Search",
            ]
        ]
        cluster_name = ""
        for indices in alias.values():
            for stats in indices:
                print_data.append(
                    [
                        stats["index_name"],
                        (opticolor.GREEN if stats["write_target"] else opticolor.RED)
                        + str(stats["write_target"])
                        + opticolor.STOP,
                        (opticolor.GREEN if stats["filter"] else opticolor.RED)
                        + str(stats["filter"])
                        + opticolor.STOP,
                        (opticolor.GREEN if stats["routing_index"] else opticolor.RED)
                        + str(stats["routing_index"])
                        + opticolor.STOP,
                        (opticolor.GREEN if stats["routing_search"] else opticolor.RED)
                        + str(stats["routing_search"])
                        + opticolor.STOP,
                    ]
                )
                cluster_name = stats["cluster_name"]
        alias_name = ""
        for name in alias.keys():
            alias_name = name
        table = AsciiTable(print_data)
        table.title = f"{alias_name} Targets (cluster: {cluster_name}) "
        print(table.table)
        print()
