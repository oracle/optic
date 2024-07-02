from terminaltables import AsciiTable

from optic.cluster.cluster import Cluster
from optic.common.config import ClusterConfig
from optic.common.exceptions import OpticDataError


def get_clusters_and_groups(config_path, clusters, search_pattern, index_types) -> list:
    """
    Uses ClusterConfig information to create list of clusters of interest
    :param config_path: path to config file
    :param clusters: list of desired clusters and cluster groups
    :param search_pattern: pattern to search for clusters
    :param index_types: dictionary of desired index types {index_type_str : reg_ex_str}
    :return: list of Cluster objects w/ auth information
    :rtype: list
    """
    config_info = ClusterConfig(config_path)
    clusters_in_groups = []
    for group, group_clusters in config_info.groups.items():
        if group in clusters:
            clusters_in_groups.extend(group_clusters)
    cluster_list = []
    for env, cluster_data in config_info.clusters.items():
        if (clusters == ()) or (env in clusters) or (env in clusters_in_groups):
            cluster_list.append(
                Cluster(
                    base_url=cluster_data["url"],
                    creds={
                        "username": cluster_data["username"],
                        "password": cluster_data["password"],
                    },
                    verify_ssl=cluster_data["verify_ssl"],
                    custom_name=env,
                    index_search_pattern=search_pattern,
                    index_types_dict=index_types,
                )
            )
    return cluster_list


def parse_bytes(bytes_string) -> int | float:
    """
    Parses a memory amount string into an integer or float
    :param bytes_string: memory amount string
    :return: int or float with parsed memory amount
    :rtype: int | float
    """
    if type(bytes_string) is float:
        return bytes_string
    if type(bytes_string) is int or bytes_string.isnumeric():
        return int(bytes_string)
    test_bytes_string = bytes_string.replace(".", "", 1)
    if test_bytes_string.isnumeric():
        return float(bytes_string)
    elif bytes_string[-1].lower() == "b":
        match bytes_string[-2].lower():
            case "k":
                if bytes_string[:-2].replace(".", "", 1).isnumeric():
                    return float(bytes_string[:-2]) * 2**10
                else:
                    raise OpticDataError("Unrecognized storage format: " + bytes_string)
            case "m":
                if bytes_string[:-2].replace(".", "", 1).isnumeric():
                    return float(bytes_string[:-2]) * 2**20
                else:
                    raise OpticDataError("Unrecognized storage format: " + bytes_string)
            case "g":
                if bytes_string[:-2].replace(".", "", 1).isnumeric():
                    return float(bytes_string[:-2]) * 2**30
                else:
                    raise OpticDataError("Unrecognized storage format: " + bytes_string)
            case "t":
                if bytes_string[:-2].replace(".", "", 1).isnumeric():
                    return float(bytes_string[:-2]) * 2**40
                else:
                    raise OpticDataError("Unrecognized storage format: " + bytes_string)
            case _:
                if bytes_string[-2].isnumeric():
                    return float(bytes_string[:-1])
                else:
                    raise OpticDataError("Unrecognized storage format: " + bytes_string)
    else:
        raise OpticDataError("Unrecognized storage format: " + bytes_string)


def parse_filters(filters) -> list:
    """
    Parses filter dictionary into list of lambdas for use with filter()
    :param filters: dictionary with filter information
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

    filter_functions = []
    for key, value in filters.items():
        if value is not None:
            if key == "min_age":
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
    :param sort_by: tuple with desired sort types
    :return: list of lambdas
    :rtype: list
    """
    sort_functions = []
    for sort_type in sort_by:
        if sort_type == "age":
            sort_functions.append(lambda index: int(index.info.age))
        elif sort_type == "name":
            sort_functions.append(lambda index: index.info.index)
        elif sort_type == "index-size":
            sort_functions.append(
                lambda index: parse_bytes(getattr(index.info, "pri.store.size"))
            )
        elif sort_type == "shard-size":
            sort_functions.append(lambda index: parse_bytes(index.info.shard_size))
        elif sort_type == "doc-count":
            sort_functions.append(lambda index: int(getattr(index.info, "docs.count")))
        elif sort_type == "type":
            sort_functions.append(lambda index: index.info.index_type)
        elif sort_type == "primary-shards":
            sort_functions.append(lambda index: int(index.info.pri))
        elif sort_type == "replica-shards":
            sort_functions.append(lambda index: int(index.info.rep))

    return sort_functions


def filter_index_list(index_list, lambda_list) -> list:
    """
    Filters index list based on lambda expressions provided
    :param index_list: list of indexes
    :param lambda_list: list of lambdas
    :return: list of filtered indexes
    :rtype: list
    """
    for function in lambda_list:
        index_list = list(filter(function, index_list))
    return index_list


def sort_index_list(index_list, lambda_list) -> list:
    """
    Sorts index list based on lambda expressions provided
    :param index_list: list of indexes
    :param lambda_list: list of lambdas
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
    :param filters: dictionary with filter information
    :param sort_by: tuple with desired sort types
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


def get_index_info(index_list) -> list:
    """
    Retrieves and packages Index information into a list of dictionaries
    :param index_list: list of Index objects
    :return: list of dictionaries containing index information
    :rtype: list
    """
    index_dicts = []
    for index in index_list:
        index_dicts.append(
            {
                "name": index.info.index,
                "age": index.info.age,
                "type": index.info.index_type,
                "count": int(getattr(index.info, "docs.count")),
                "index_size": getattr(index.info, "pri.store.size"),
                "shard_size": index.info.shard_size,
                "pri": int(index.info.pri),
                "rep": int(index.info.rep),
                "cluster": index.cluster_name,
            }
        )
    return index_dicts


def print_index_info(index_dicts) -> None:
    """
    Print Index Info
    :param dict index_dicts: list of dictionaries of index information
    :return: None
    :rtype: None
    """

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
                stats["cluster"],
            ]
        )

    table = AsciiTable(print_data)
    table.title = "Index Info"
    print(table.table)
