from optic.cluster.cluster import Cluster, ClusterHealth


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
        assert test_cluster.health.task_max_waiting_in_queue_mill == 0
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
