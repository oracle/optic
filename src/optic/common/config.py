# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

import os

import yaml

from optic.cluster.cluster import Cluster
from optic.common.exceptions import OpticConfigurationFileError


def yaml_load(file_path) -> dict:
    """
    Parses yaml file for information

    return: File information as Python object
    rtype: dict
    :raises OpticConfigurationFileError: if yaml file cannot be parsed
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
    def __init__(
        self,
        cluster_data=None,
        selected_clusters=None,
        selected_cluster_properties=None,
    ):
        self._data = cluster_data or {}
        self._selected_clusters = selected_clusters or []
        self._selected_cluster_properties = selected_cluster_properties or {}
        self._groups = None
        self._clusters = None
        self._selected_cluster_objects = None

    @property
    def groups(self) -> dict:
        """
        Gets cluster group information from data

        :return: Dictionary of cluster group information
        :rtype: dict
        """
        if self._groups is None:
            self._groups = self._data.get("groups", None)
        return self._groups

    @property
    def clusters(self) -> dict:
        """
        Gets cluster information from data

        :return: Dictionary of cluster information
        :rtype: dict
        """
        if self._clusters is None:
            try:
                self._clusters = self._data["clusters"]
            except KeyError as err:
                raise OpticConfigurationFileError(
                    "Missing clusters key in configuration information"
                ) from err
        return self._clusters

    @property
    def selected_cluster_objects(self) -> list[Cluster]:
        """
        Makes list of cluster objects from depending on desired

        :return: List of cluster objects
        :rtype: list[Cluster]
        """
        if self._selected_cluster_objects is None:
            self._selected_cluster_objects = []

            # Replaces cluster group names with associated clusters
            if self.groups:
                for group_name, group_clusters in self.groups.items():
                    if group_name in self._selected_clusters:
                        self._selected_clusters.extend(group_clusters)
                        self._selected_clusters.remove(group_name)
            # Delete repeats
            self._selected_clusters = list(set(self._selected_clusters))

            # If no clusters specified, do all clusters
            default_behavior = len(self._selected_clusters) == 0

            # If a cluster is in desired cluster list, makes object out of it
            for cluster_name, cluster_data in self.clusters.items():
                if (cluster_name in self._selected_clusters) or default_behavior:
                    try:
                        do_ssl = cluster_data.get("verify_ssl", True)
                        if type(do_ssl) is not bool:
                            raise OpticConfigurationFileError(
                                "Unrecognized SSL option for " + cluster_name
                            )
                        new_cluster = Cluster(
                            base_url=cluster_data["url"],
                            creds={
                                "username": cluster_data["username"],
                                "password": cluster_data["password"],
                            },
                            verify_ssl=do_ssl,
                            custom_name=cluster_name,
                        )
                        # Adds all extra properties from _desired_cluster_properties
                        for (
                            attribute,
                            value,
                        ) in self._selected_cluster_properties.items():
                            if attribute not in new_cluster.__dict__:
                                raise OpticConfigurationFileError(
                                    "Non-existent attribute "
                                    + attribute
                                    + " specified in desired_cluster_properties"
                                )
                            setattr(new_cluster, attribute, value)
                        self._selected_cluster_objects.append(new_cluster)
                        if self._selected_clusters:
                            self._selected_clusters.remove(cluster_name)
                    except KeyError as e:
                        raise OpticConfigurationFileError(
                            "Improperly formatted fields in cluster " + cluster_name
                        ) from e
            # Notifies if any non-existent clusters provided
            for error_cluster in self._selected_clusters:
                print(
                    error_cluster, "is not present in cluster configuration information"
                )
        return self._selected_cluster_objects


class Settings:
    def __init__(self, settings_data):
        self.fields = settings_data
