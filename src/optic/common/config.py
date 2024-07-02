import json
import os

import yaml

from optic.common.exceptions import OpticConfigurationFileError


class ClusterConfig:
    def __init__(self, config_path):
        self.config_path = config_path
        self._json_data = self._load()
        self._groups = None
        self._clusters = None

    def _load(self) -> list:
        """
        Parses config file for cluster information
        :return: Dictionary with cluster information
        :rtype: dict
        """
        try:
            abs_path = os.path.expanduser(self.config_path)
            config_file = open(abs_path)
            json_data = json.load(config_file)
        except Exception as e:
            if type(e) is json.decoder.JSONDecodeError:
                config_file.close()
            raise OpticConfigurationFileError(
                "Non-existent or improperly formatted configuration file at " + abs_path
            ) from e
        return json_data

    @property
    def groups(self):
        if self._groups is None:
            try:
                self._groups = self._json_data["groups"]
            except KeyError as err:
                raise OpticConfigurationFileError(
                    "Missing groups key in configuration file"
                ) from err
        return self._groups

    @property
    def clusters(self):
        if self._clusters is None:
            try:
                self._clusters = self._json_data["clusters"]
            except KeyError as err:
                raise OpticConfigurationFileError(
                    "Missing clusters key in configuration file"
                ) from err
        return self._clusters


class Settings:
    def __init__(self, config_path):
        self.config_path = config_path
        self.fields = self._load()

    def _load(self) -> list:
        """
        Parses config file for settings information
        return: Dictionary with settings information
        rtype: dict
        """
        try:
            abs_path = os.path.expanduser(self.config_path)
            config_file = open(abs_path)
            yaml_data = yaml.safe_load(config_file)
        except Exception as e:
            if type(e) is yaml.YAMLError:
                config_file.close()
            raise OpticConfigurationFileError(
                "Non-existent or improperly formatted settings file at " + abs_path
            ) from e
        return yaml_data
