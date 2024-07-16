import os

import yaml

from optic.cluster.cluster import Cluster
from optic.common.exceptions import OpticConfigurationFileError


def yaml_load(file_path) -> list:
    """
    Parses yaml file for information
    return: Dictionary with information
    rtype: dict
    """
    try:
        abs_path = os.path.expanduser(file_path)
        config_file = open(abs_path)
        yaml_data = yaml.safe_load(config_file)
    except Exception as e:
        if type(e) is yaml.YAMLError:
            config_file.close()
        raise OpticConfigurationFileError(
            "Non-existent or improperly formatted file at " + abs_path
        ) from e
    return yaml_data


class ClusterConfig:
    def __init__(self, cluster_data, desired_clusters, desired_cluster_properties):
        self._data = cluster_data
        self._desired_clusters = desired_clusters
        self._desired_cluster_properties = desired_cluster_properties
        self._groups = None
        self._clusters = None
        self._desired_cluster_objects = None

    @property
    def groups(self):
        if self._groups is None:
            try:
                self._groups = self._data["groups"]
            except KeyError as err:
                raise OpticConfigurationFileError(
                    "Missing groups key in configuration information"
                ) from err
        return self._groups

    @property
    def clusters(self):
        if self._clusters is None:
            try:
                self._clusters = self._data["clusters"]
            except KeyError as err:
                raise OpticConfigurationFileError(
                    "Missing clusters key in configuration information"
                ) from err
        return self._clusters

    @property
    def desired_cluster_objects(self):
        if self._desired_cluster_objects is None:
            self._desired_cluster_objects = []

            # Replaces cluster group names with associated clusters
            for group_name, group_clusters in self.groups.items():
                if group_name in self._desired_clusters:
                    self._desired_clusters.extend(group_clusters)
                    self._desired_clusters.remove(group_name)
            self._desired_clusters = list(set(self._desired_clusters))

            # If no clusters specified, do all clusters TODO: DECIDE DEFAULT BEHAVIOR
            default_behavior = len(self._desired_clusters) == 0

            # If a cluster is in desired cluster list, makes object out of it
            for cluster_name, cluster_data in self.clusters.items():
                if (cluster_name in self._desired_clusters) or default_behavior:
                    try:
                        new_cluster = Cluster(
                            base_url=cluster_data["url"],
                            creds={
                                "username": cluster_data["username"],
                                "password": cluster_data["password"],
                            },
                            verify_ssl=cluster_data["verify_ssl"],
                            custom_name=cluster_name,
                        )
                        # Adds all extra properties from _desired_cluster_properties
                        for (
                            attribute,
                            value,
                        ) in self._desired_cluster_properties.items():
                            if attribute not in new_cluster.__dict__:
                                raise OpticConfigurationFileError(
                                    "Non-existent attribute "
                                    + attribute
                                    + " specified in desired_cluster_properties"
                                )
                            setattr(new_cluster, attribute, value)
                        self._desired_cluster_objects.append(new_cluster)
                        if self._desired_clusters:
                            self._desired_clusters.remove(cluster_name)
                    except KeyError as e:
                        raise OpticConfigurationFileError(
                            "Improperly formatted fields in cluster " + cluster_name
                        ) from e
            # Notifies if any non-existent clusters provided
            for error_cluster in self._desired_clusters:
                print(
                    error_cluster, "is not present in cluster configuration information"
                )
        return self._desired_cluster_objects


class Settings:
    def __init__(self, settings_data):
        self.fields = settings_data
