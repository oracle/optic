import pytest

from optic.cluster.cluster import Cluster, ClusterHealth
from optic.cluster.cluster_service import (
    build_cluster_info_table,
    get_cluster_info,
    get_selected_clusters,
)
from optic.common.optic_color import OpticColor


@pytest.fixture
def cluster_selection():
    cluster_1 = Cluster(name="test_cluster_1")
    cluster_1._storage_percent = 17
    cluster_1._health = ClusterHealth(**{"status": "green"})
    cluster_2 = Cluster(name="test_cluster_2")
    cluster_2._storage_percent = 74
    cluster_2._health = ClusterHealth(**{"status": "yellow"})
    cluster_3 = Cluster(name="test_cluster_3")
    cluster_3._storage_percent = 59
    cluster_3._health = ClusterHealth(**{"status": "yellow"})
    return [cluster_1, cluster_2, cluster_3]


class TestClusterClass:
    def test_cluster_health(self):
        test_cluster = Cluster(name="test_cluster")
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
        test_cluster = Cluster(name="test_cluster")
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


class TestClusterService:
    def test_get_cluster_info(self, cluster_selection):

        cluster_info = get_cluster_info(cluster_selection)
        assert cluster_info[0]["name"] == "test_cluster_1"
        assert cluster_info[1]["name"] == "test_cluster_2"
        assert cluster_info[2]["name"] == "test_cluster_3"
        assert cluster_info[0]["status"] == "green"
        assert cluster_info[1]["status"] == "yellow"
        assert cluster_info[2]["status"] == "yellow"
        assert cluster_info[0]["usage"] == 17
        assert cluster_info[1]["usage"] == 74
        assert cluster_info[2]["usage"] == 59

    def test_build_cluster_info_table_valid_cluster_color(
        self, cluster_selection, optic_settings
    ):
        optic_color = OpticColor()
        cluster_info = get_cluster_info(cluster_selection)
        table = build_cluster_info_table(
            cluster_info, True, optic_settings["storage_percent_thresholds"]
        )
        assert table.table is not None
        assert all(cluster.name in table.table for cluster in cluster_selection)
        assert optic_color.GREEN in table.table
        assert optic_color.YELLOW in table.table
        assert optic_color.RED not in table.table

    @pytest.mark.skip(reason="disabling of colors is broken")
    def test_build_cluster_info_table_valid_cluster_no_color(
        self, cluster_selection, optic_settings
    ):
        optic_color = OpticColor()
        optic_color.disable_colors()

        cluster_info = get_cluster_info(cluster_selection)
        table = build_cluster_info_table(
            cluster_info, True, optic_settings["storage_percent_thresholds"]
        )
        assert table.table is not None
        assert all(cluster.name in table.table for cluster in cluster_selection)
        assert optic_color.GREEN not in table.table
        assert optic_color.YELLOW not in table.table

    def test_build_cluster_info_table_invalid_cluster(
        self, cluster_config, optic_settings
    ):
        selected_clusters = get_selected_clusters(cluster_config, ["cluster_4"])
        cluster_info = get_cluster_info(selected_clusters)
        assert len(cluster_info) == 0
        assert (
            build_cluster_info_table(
                cluster_info,
                optic_settings["disable_terminal_color"],
                optic_settings["storage_percent_thresholds"],
            )
        ) is None
