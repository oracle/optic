from terminaltables import AsciiTable

from optic.cluster.cluster import Cluster
from optic.common.config import ClusterConfig
from optic.common.exceptions import OpticConfigurationFileError


def get_cluster_list(config_path, byte_type) -> list:
    """
    Uses ClusterConfig information to create list of clusters of interest
    :param config_path: path to optic config file
    :param byte_type: desired byte type for storage calculation
    :return: list of Cluster objects w/ auth information
    :rtype: list
    """
    config_info = ClusterConfig(config_path)
    cluster_list = []
    for env, cluster_data in config_info.clusters.items():
        try:
            cluster_list.append(
                Cluster(
                    base_url=cluster_data["url"],
                    creds={
                        "username": cluster_data["username"],
                        "password": cluster_data["password"],
                    },
                    verify_ssl=cluster_data["verify_ssl"],
                    custom_name=env,
                    byte_type=byte_type,
                )
            )
        except KeyError as e:
            raise OpticConfigurationFileError(
                "Improperly formatted fields in cluster " + env
            ) from e
    return cluster_list


def get_cluster_info(cluster_list) -> list:
    """
    Retrieves and packages Cluster information into a list of dictionaries
    :param cluster_list: list of Cluster objects
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
    Print Cluster Info
    :param cluster_dicts: dictionary of cluster information
    :return: None
    :rtype: None
    """
    print_data = [["ENV", "STATUS", "STORAGE USE (%)"]]
    for stats in cluster_dicts:
        print_data.append([stats["name"], stats["status"], stats["usage"]])

    table = AsciiTable(print_data)
    table.title = "Cluster Info"
    print(table.table)
