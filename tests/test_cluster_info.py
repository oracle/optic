import pytest

from optic.cluster.cluster import Cluster, ClusterHealth
from optic.cluster.cluster_service import build_cluster_info_table, get_cluster_info
from optic.common.config import ClusterConfig


class TestClusterClass:
    def test_cluster_health(self):
        test_cluster = Cluster(custom_name="test_cluster")
        sim_health_response = {
            "cluster_name": "x12",
            "status": "yellow",
            "timed_out": False,
            "number_of_nodes": 2,
            "number_of_data_nodes": 1,
            "discovered_master": True,
            "discovered_cluster_manager": True,
            "active_primary_shards": 46,
            "active_shards": 46,
            "relocating_shards": 0,
            "initializing_shards": 0,
            "unassigned_shards": 35,
            "delayed_unassigned_shards": 0,
            "number_of_pending_tasks": 0,
            "number_of_in_flight_fetch": 0,
            "task_max_waiting_in_queue_millis": 0,
            "active_shards_percent_as_number": 56.79012345679012,
        }
        test_cluster._health = ClusterHealth(**sim_health_response)

        assert test_cluster.health.cluster_name == "x12"
        assert test_cluster.health.status == "yellow"
        assert test_cluster.health.timed_out is False
        assert test_cluster.health.number_of_nodes == 2
        assert test_cluster.health.number_of_data_nodes == 1
        assert test_cluster.health.discovered_master is True
        assert test_cluster.health.discovered_cluster_manager is True
        assert test_cluster.health.active_primary_shards == 46
        assert test_cluster.health.active_shards == 46
        assert test_cluster.health.relocating_shards == 0
        assert test_cluster.health.initializing_shards == 0
        assert test_cluster.health.unassigned_shards == 35
        assert test_cluster.health.delayed_unassigned_shards == 0
        assert test_cluster.health.number_of_pending_tasks == 0
        assert test_cluster.health.number_of_in_flight_fetch == 0
        assert test_cluster.health.task_max_waiting_in_queue_millis == 0
        assert test_cluster.health.active_shards_percent_as_number == 56.79012345679012

    def test_storage_percent(self):
        test_cluster = Cluster(custom_name="test_cluster")
        sim_disk_response = [
            {"disk.used": "505", "disk.total": "50216"},
            {"disk.used": None, "disk.total": None},
        ]
        assert test_cluster._calculate_storage_percent(sim_disk_response) == 1
        sim_disk_response = [
            {"disk.used": "142", "disk.total": "145"},
            {"disk.used": None, "disk.total": None},
            {"disk.used": "22", "disk.total": 334},
        ]
        assert test_cluster._calculate_storage_percent(sim_disk_response) == 34


@pytest.fixture
def selected_clusters():
    cluster_1 = Cluster(custom_name="test_cluster_1")
    cluster_1._storage_percent = 17
    cluster_1._health = ClusterHealth(**{"status": "green"})
    cluster_2 = Cluster(custom_name="test_cluster_2")
    cluster_2._storage_percent = 74
    cluster_2._health = ClusterHealth(**{"status": "yellow"})
    cluster_3 = Cluster(custom_name="test_cluster_3")
    cluster_3._storage_percent = 59
    cluster_3._health = ClusterHealth(**{"status": "yellow"})
    return [cluster_1, cluster_2, cluster_3]


@pytest.fixture
def config_info(cluster_config):
    return ClusterConfig(cluster_config)


class TestClusterService:
    def test_get_cluster_info(self, config_info, selected_clusters):
        config_info._selected_cluster_objects = selected_clusters
        cluster_dict = get_cluster_info(config_info)
        assert cluster_dict[0]["name"] == "test_cluster_1"
        assert cluster_dict[1]["name"] == "test_cluster_2"
        assert cluster_dict[2]["name"] == "test_cluster_3"
        assert cluster_dict[0]["status"] == "green"
        assert cluster_dict[1]["status"] == "yellow"
        assert cluster_dict[2]["status"] == "yellow"
        assert cluster_dict[0]["usage"] == 17
        assert cluster_dict[1]["usage"] == 74
        assert cluster_dict[2]["usage"] == 59

    def test_build_cluster_info_table_valid_cluster(
        self, config_info, selected_clusters, optic_settings
    ):
        os = optic_settings
        config_info._selected_cluster_objects = selected_clusters
        cluster_info = get_cluster_info(config_info)
        table = build_cluster_info_table(
            cluster_info, os["disable_terminal_color"], os["storage_percent_thresholds"]
        )
        assert table.table is not None
        assert all(cluster.custom_name in table.table for cluster in selected_clusters)

    def test_build_cluster_info_table_invalid_cluster(
        self, cluster_config, optic_settings
    ):
        config_info = ClusterConfig(cluster_config, ["cluster_4"])
        os = optic_settings
        cluster_info = get_cluster_info(config_info)
        assert len(config_info.selected_cluster_objects) == 0
        assert (
            build_cluster_info_table(
                cluster_info,
                os["disable_terminal_color"],
                os["storage_percent_thresholds"],
            )
        ) is None
