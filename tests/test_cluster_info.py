from optic.cluster.cluster_info import get_cluster_info


class TestClusterInfo:
    def test_get_cluster_info(self):
        cluster_name = "test_cluster"
        cluster_info = get_cluster_info(cluster_name)
        assert cluster_info is not None
        assert len(cluster_info)
        assert cluster_info == f"Hello OPTIC Cluster info for: {cluster_name}"
