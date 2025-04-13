import shutil
import tempfile

import pytest
import yaml


@pytest.fixture
def ctx_obj(optic_settings_file_path):
    yield {"settings_file_path": optic_settings_file_path}


@pytest.fixture
def cluster_config_file_path():
    temp_dir = tempfile.mkdtemp()
    settings_file_path = f"{temp_dir}/cluster-config.yaml"

    with open(settings_file_path, "w") as f:
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

    yield settings_file_path

    # Clean up the temporary directory and its contents
    shutil.rmtree(temp_dir)


@pytest.fixture
def optic_settings_file_path(cluster_config_file_path):
    temp_dir = tempfile.mkdtemp()
    settings_file_path = f"{temp_dir}/optic-settings.yaml"

    with open(settings_file_path, "w") as f:
        yaml.dump(
            {
                "default_cluster_config_file_path": cluster_config_file_path,
                "default_cluster_info_byte_type": "gb",
                "default_index_type_patterns": {
                    "DATED": r"(.*)-(\d{4})\.(\d{2})\.(\d{2})$",
                    "ISM": r"(.*)-ism-(\d{6})$",
                    "ISM_MALFORMED": "(.*)-ism$",
                    "STATIC": "(.*)_static(.*)$",
                    "SYSTEM": r"(^\..*)$",
                },
                "default_search_pattern": "*",
                "disable_terminal_color": False,
                "settings_file_path": {settings_file_path},
                "storage_percent_thresholds": {"GREEN": 80, "RED": 100, "YELLOW": 85},
            },
            f,
        )

    yield settings_file_path

    # Clean up the temporary directory and its contents
    shutil.rmtree(temp_dir)


@pytest.fixture
def optic_settings(optic_settings_file_path) -> dict:
    with open(optic_settings_file_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture
def cluster_config(cluster_config_file_path) -> dict:
    with open(cluster_config_file_path, "r") as f:
        return yaml.safe_load(f)
