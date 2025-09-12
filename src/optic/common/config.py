# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

import os

import yaml

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


def read_cluster_config(cluster_config_file_path):
    return ClusterConfig(yaml_load(cluster_config_file_path))


class ClusterConfig:
    def __init__(
        self,
        yaml=None,
    ):
        self._yaml = yaml or {}
        self._groups = None
        self._clusters = None

    @property
    def groups(self) -> dict:
        """
        Extracts cluster group information from yaml input

        :return: Dictionary of cluster groups defined within the input yaml
        :rtype: dict
        """
        if self._groups is None:
            self._groups = self._yaml.get("groups", None)
        return self._groups

    @property
    def clusters(self) -> dict:
        """
        Extracts cluster information from yaml input

        :return: Dictionary of clusters defined within the input yaml
        :rtype: dict
        """
        if self._clusters is None:
            try:
                self._clusters = self._yaml["clusters"]
            except KeyError as err:
                raise OpticConfigurationFileError(
                    "Missing clusters key in configuration information"
                ) from err
        return self._clusters


class OpticSettings:
    def __init__(self, settings_data):
        self.fields = settings_data
