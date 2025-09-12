import shutil
import tempfile

import pytest
import yaml

from optic.common.config import ClusterConfig


@pytest.fixture
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Clean up the temporary directory and its contents
    shutil.rmtree(temp_dir)


@pytest.fixture
def cluster_config_file_path(temp_dir):
    return f"{temp_dir}/cluster-config.yaml"


@pytest.fixture
def optic_settings_file_path(temp_dir):
    return f"{temp_dir}/optic-settings.yaml"


@pytest.fixture
def cluster_config_file(cluster_config_file_path):

    with open(cluster_config_file_path, "w") as f:
        yaml.dump(
            {
                "clusters": {
                    "cluster_1": {
                        "url": "https://testurl.com:46",
                        "username": "my_username1",
                        "password": "my_password",
                    },
                    "cluster_2": {
                        "url": "https://myurl.com:9200",
                        "username": "my_username2",
                        "password": "****",
                    },
                    "my_cluster": {
                        "url": "https://testurl.com:46",
                        "username": "my_username1",
                        "password": "****",
                    },
                    "cluster_3": {
                        "url": "https://testurl.com:46",
                        "username": "my_username1",
                        "password": "****",
                    },
                },
                "groups": {
                    "my_group": [
                        "cluster_1",
                        "cluster_3",
                        "cluster_3",
                    ],
                    "g2": ["cluster_1", "my_cluster"],
                },
            },
            f,
        )

    yield cluster_config_file_path


@pytest.fixture
def optic_settings_file(optic_settings_file_path, cluster_config_file_path):

    with open(optic_settings_file_path, "w") as f:
        yaml.dump(
            {
                "cluster_config_file": cluster_config_file_path,
                "disable_terminal_color": False,
                "search_pattern": "*",
                "byte_type": "gb",
                "storage_percent_thresholds": {"GREEN": 80, "RED": 100, "YELLOW": 85},
                "index_type_patterns": {
                    "DATED": r"(.*)-(\d{4})\.(\d{2})\.(\d{2})$",
                    "ISM": r"(.*)-ism-(\d{6})$",
                    "ISM_MALFORMED": "(.*)-ism$",
                    "STATIC": "(.*)_static(.*)$",
                    "SYSTEM": r"(^\..*)$",
                },
            },
            f,
        )

    yield optic_settings_file_path


@pytest.fixture
def optic_settings(optic_settings_file) -> dict:
    with open(optic_settings_file, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture
def cluster_config(cluster_config_file) -> dict:
    with open(cluster_config_file, "r") as f:
        return ClusterConfig(yaml.safe_load(f))
