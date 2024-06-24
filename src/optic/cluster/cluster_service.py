from optic.cluster.cluster import Cluster
from optic.common.config import Config
from optic.common.exceptions import ConfigurationFileError

from terminaltables import AsciiTable


def get_cluster_list(config_path, byte_type) -> [Cluster]:
    """
    Parses file for cluster configuration information
    :param config_path: path to optic config file
    :param byte_type: desired byte type for storage calculation
    :return: list of Cluster objects w/ auth information
    :rtype: list of Cluster objects
    """
    config_info = Config(config_path)
    cluster_list = []
    for env, auth_data in config_info.clusters.items():
        try:
            cluster_list.append(
                Cluster(
                    base_url=auth_data["url"],
                    creds={
                        "username": auth_data["username"],
                        "password": auth_data["password"],
                    },
                    verify_ssl=auth_data["verify_ssl"],
                    custom_name=env,
                    byte_type=byte_type,
                )
            )
        except KeyError as e:
            raise ConfigurationFileError(
                "Improperly formatted fields in cluster " + env
            ) from e
    return cluster_list


def package_cluster_info(cluster_list) -> {}:
    """
    Retrieves and packages Cluster information into a JSON object
    :param cluster_list: list of Cluster objects
    :return: JSON object containing cluster information
    :rtype: dict
    """
    clusters_dict = {}
    for cluster in cluster_list:
        usage = cluster.storage_percent
        status = cluster.health.status
        clusters_dict[cluster.custom_name] = {"status": status, "usage": usage}
    return clusters_dict


def print_cluster_info(json_object) -> None:
    """
    Print Cluster Info
    :param dict json_object: json object of cluster information
    :return: None
    :rtype: None
    """
    print_data = [["ENV", "STATUS", "STORAGE USE (%)"]]
    for env, stats in json_object.items():
        print_data.append([env, stats["status"], stats["usage"]])

    table = AsciiTable(print_data)
    table.title = "Cluster Info"
    print(table.table)
