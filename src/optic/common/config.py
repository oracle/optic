import os
import json


class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self._json_data = self._load(config_path)
        self._groups = None
        self._clusters = None


    def _load(self, config_path):
        config_file = open(os.path.expanduser(config_path))
        json_data = json.load(config_file)
        return json_data

    @property
    def groups(self):
        if self._groups is None:
            self._groups = self._json_data['groups']
        return self._groups

    @property
    def clusters(self):
        if self._clusters is None:
            self._clusters = self._json_data['clusters']
        return self._clusters
