# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

from terminaltables import AsciiTable

from optic.common.exceptions import OpticDataError
from optic.common.optic_color import OpticColor


def parse_bytes(bytes_string) -> int | float:
    """
    Parses a memory amount string into an integer or float

    :param str|float|int bytes_string: memory amount string
    :return: int or float with parsed memory amount
    :rtype: int | float
    :raises OpticDataError: if the memory amount string format is not valid
    """
    if type(bytes_string) is float:
        return bytes_string
    if type(bytes_string) is int or bytes_string.isdigit():
        return int(bytes_string)
    no_decimal_string = bytes_string.replace(".", "", 1)
    if no_decimal_string.isdigit():
        return float(bytes_string)
    elif bytes_string[-1].lower() == "b":
        match bytes_string[-2].lower():
            case "k":
                if no_decimal_string[:-2].isdigit():
                    return float(bytes_string[:-2]) * 2**10
            case "m":
                if no_decimal_string[:-2].isdigit():
                    return float(bytes_string[:-2]) * 2**20
            case "g":
                if no_decimal_string[:-2].isdigit():
                    return float(bytes_string[:-2]) * 2**30
            case "t":
                if no_decimal_string[:-2].isdigit():
                    return float(bytes_string[:-2]) * 2**40
            case _:
                if no_decimal_string[-2].isdigit():
                    return float(bytes_string[:-1])
        raise OpticDataError("Unrecognized storage format: " + bytes_string)
    else:
        raise OpticDataError("Unrecognized storage format: " + bytes_string)


def parse_filters(filters) -> list:
    """
    Parses filter dictionary into list of lambdas for use with filter()

    :param dict filters: dictionary with filter information
    :return: list of lambdas
    :rtype: list
    """

    def filter_generator(attribute, captured_value, filter_type):
        if filter_type == "max":
            return lambda index: (
                parse_bytes(getattr(index.info, attribute))
                <= parse_bytes(captured_value)
            )
        elif filter_type == "min":
            return lambda index: (
                parse_bytes(getattr(index.info, attribute))
                >= parse_bytes(captured_value)
            )
        elif filter_type == "equality":
            return lambda index: (getattr(index.info, attribute) != captured_value)
        elif filter_type == "top_level":
            return lambda index: (getattr(index, attribute) == captured_value)

    filter_functions = []
    for key, value in filters.items():
        if value is not None:
            if key == "write_alias_only":
                filter_functions.append(
                    filter_generator("write_alias", value, "top_level")
                )
            elif key == "min_age":
                filter_functions.append(filter_generator("age", value, "min"))
            elif key == "max_age":
                filter_functions.append(filter_generator("age", value, "max"))
            elif key == "min_index_size":
                filter_functions.append(
                    filter_generator("pri.store.size", value, "min")
                )
            elif key == "max_index_size":
                filter_functions.append(
                    filter_generator("pri.store.size", value, "max")
                )
            elif key == "min_shard_size":
                filter_functions.append(filter_generator("shard_size", value, "min"))
            elif key == "max_shard_size":
                filter_functions.append(filter_generator("shard_size", value, "max"))
            elif key == "min_doc_count":
                filter_functions.append(filter_generator("docs.count", value, "min"))
            elif key == "max_doc_count":
                filter_functions.append(filter_generator("docs.count", value, "max"))
            elif key == "type_filter":
                for type_filter in value:
                    filter_functions.append(
                        filter_generator("index_type", type_filter, "equality")
                    )
    return filter_functions


def parse_sort_by(sort_by) -> list:
    """
    Parses tuple of desired sort into list of lambdas for use as sort() keys

    :param list sort_by: tuple with desired sort types
    :return: list of lambdas
    :rtype: list
    """
    sort_functions = []
    for sort_type in sort_by:
        if sort_type == "age":
            sort_functions.append(lambda index: index.info.age)
        elif sort_type == "name":
            sort_functions.append(lambda index: index.info.index)
        elif sort_type == "write-alias":
            sort_functions.append(lambda index: index.write_alias)
        elif sort_type == "index-size":
            sort_functions.append(
                lambda index: parse_bytes(getattr(index.info, "pri.store.size"))
            )
        elif sort_type == "shard-size":
            sort_functions.append(lambda index: parse_bytes(index.info.shard_size))
        elif sort_type == "doc-count":
            sort_functions.append(lambda index: getattr(index.info, "docs.count"))
        elif sort_type == "type":
            sort_functions.append(lambda index: index.info.index_type)
        elif sort_type == "primary-shards":
            sort_functions.append(lambda index: index.info.pri)
        elif sort_type == "replica-shards":
            sort_functions.append(lambda index: index.info.rep)

    return sort_functions


def filter_index_list(index_list, lambda_list) -> list:
    """
    Filters index list based on lambda expressions provided

    :param list index_list: list of indexes
    :param list lambda_list: list of lambdas
    :return: list of filtered indexes
    :rtype: list
    """
    for function in lambda_list:
        index_list = list(filter(function, index_list))
    return index_list


def sort_index_list(index_list, lambda_list) -> list:
    """
    Sorts index list based on lambda expressions provided

    :param list index_list: list of indexes
    :param list lambda_list: list of lambdas
    :return: list of sorted indexes
    :rtype: list
    """
    for function in lambda_list:
        index_list.sort(key=function)
    return index_list


def filter_and_sort_indices(cluster_list, filters, sort_by) -> list:
    """
    Retrieves, filters, and sorts indexes from clusters

    :param cluster_list: list of clusters
    :param dict filters: dictionary with filter information
    :param list sort_by: tuple with desired sort types
    :return: list of filtered indexes
    :rtype: list
    """
    index_list = []
    for cluster in cluster_list:
        index_list.extend(cluster.index_list)

    filter_functions = parse_filters(filters)
    sort_by_functions = parse_sort_by(sort_by)

    index_list = filter_index_list(index_list, filter_functions)
    index_list = sort_index_list(index_list, sort_by_functions)
    return index_list


def get_index_info(config_info, filters=None, sort_by=None) -> list:
    """
    Retrieves and packages Index information into a list of dictionaries

    :param ClusterConfig config_info: Cluster Configuration info object
    :param dict filters: dictionary with filter information
    :param list sort_by: tuple with desired sort types
    :return: list of dictionaries containing index information
    :rtype: list
    """
    if filters is None:
        filters = {
            "write_alias_only": None,
            "min_age": None,
            "max_age": None,
            "min_index_size": None,
            "max_index_size": None,
            "min_shard_size": None,
            "max_shard_size": None,
            "min_doc_count": None,
            "max_doc_count": None,
            "type_filter": [],
        }
    if sort_by is None:
        sort_by = []
    index_list = filter_and_sort_indices(
        config_info.selected_cluster_objects, filters, sort_by
    )
    index_dicts = []
    for index in index_list:
        index_dicts.append(
            {
                "name": index.info.index,
                "write_alias": index.write_alias,
                "age": index.info.age,
                "type": index.info.index_type,
                "count": getattr(index.info, "docs.count"),
                "index_size": getattr(index.info, "pri.store.size"),
                "shard_size": index.info.shard_size,
                "pri": index.info.pri,
                "rep": index.info.rep,
                "cluster": index.cluster_name,
            }
        )
    return index_dicts


def print_index_info(index_dicts, no_color) -> None:
    """
    Prints Index Information

    :param list index_dicts: list of dictionaries of index information
    :param bool no_color: whether colored output or not
    :return: None
    :rtype: None
    """
    optic_color = OpticColor()
    if no_color:
        optic_color.disable_colors()

    print_data = [
        [
            "Index",
            "Age",
            "Type",
            "Document Count",
            "Index Size",
            "Shard Size",
            "Pri",
            "Rep",
            "Write Alias",
            "Cluster",
        ]
    ]
    for stats in index_dicts:
        print_data.append(
            [
                stats["name"],
                stats["age"],
                stats["type"],
                stats["count"],
                stats["index_size"],
                stats["shard_size"],
                stats["pri"],
                stats["rep"],
                (optic_color.GREEN if stats["write_alias"] else optic_color.RED)
                + str(stats["write_alias"])
                + optic_color.STOP,
                stats["cluster"],
            ]
        )

    table = AsciiTable(print_data)
    table.title = "Index Info"
    print(table.table)
