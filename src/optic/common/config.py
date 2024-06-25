import os
import json
from optic.common.exceptions import ConfigurationFileError


class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self._json_data = self._load(config_path)
        self._groups = None
        self._clusters = None

    def _load(self, config_path):
        try:
            abs_path = os.path.expanduser(config_path)
            config_file = open(abs_path)
            json_data = json.load(config_file)
        except Exception as e:
            if type(e) is json.decoder.JSONDecodeError:
                config_file.close()
            raise ConfigurationFileError(
                "Non-existent or improperly formatted configuration file at " + abs_path
            ) from e
        return json_data

    @property
    def groups(self):
        if self._groups is None:
            try:
                self._groups = self._json_data["groups"]
            except KeyError as err:
                raise ConfigurationFileError(
                    "Missing groups key in configuration file"
                ) from err
        return self._groups

    @property
    def clusters(self):
        if self._clusters is None:
            try:
                self._clusters = self._json_data["clusters"]
            except KeyError as err:
                raise ConfigurationFileError(
                    "Missing clusters key in configuration file"
                ) from err
        return self._clusters
