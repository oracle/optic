from optic.common.api import OpenSearchAction
from optic.common.exceptions import OpticDataError
from optic.index.index import Index, IndexInfo


class ClusterHealth:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Cluster:
    def __init__(
        self,
        base_url=None,
        creds=None,
        verify_ssl=True,
        custom_name=None,
        byte_type=None,
        index_search_pattern=None,
        index_types_dict=None,
    ):
        self.base_url = base_url
        self.creds = creds
        self.verify_ssl = verify_ssl

        self.custom_name = custom_name
        self.byte_type = byte_type
        self._health = None
        self._storage_percent = None
        self.index_search_pattern = index_search_pattern
        self._index_list = None
        self.index_types_dict = index_types_dict

    def _calculate_storage_percent(self, disk_list) -> int:
        """
        Calculate the storage percentage of cluster in use
        :param disk_list: dictionary of cluster disk information
        :return: storage percentage (0-100)
        :rtype: int
        """
        used = 0
        total = 0
        for disk in disk_list:
            if disk["disk.used"] is None or disk["disk.total"] is None:
                pass
            else:
                used += int(disk["disk.used"])
                total += int(disk["disk.total"])
        if total == 0:
            raise OpticDataError(
                f"Error in [{self.custom_name}] disk capacity calculation"
                "(Total disk capacity is 0 or null)"
            )
        return int(round(100 * (float(used) / float(total))))

    @property
    def health(self) -> dict:
        if not self._health:
            print("Getting cluster health")
            api = OpenSearchAction(
                base_url=self.base_url,
                usr=self.creds["username"],
                pwd=self.creds["password"],
                verify_ssl=self.verify_ssl,
                query="/_cluster/health?pretty",
            )
            self._health = ClusterHealth(**api.response)

        return self._health

    @property
    def storage_percent(self) -> int:
        if not self._storage_percent:
            print("Getting storage percent")
            api = OpenSearchAction(
                base_url=self.base_url,
                usr=self.creds["username"],
                pwd=self.creds["password"],
                verify_ssl=self.verify_ssl,
                query="/_cat/allocation?h=disk.used,"
                "disk.total&format=json&bytes=" + self.byte_type,
            )
            self._storage_percent = self._calculate_storage_percent(api.response)

        return self._storage_percent

    @property
    def index_list(self) -> list:
        if not self._index_list:
            print("Getting cluster index list")
            index_list = []
            api = OpenSearchAction(
                base_url=self.base_url,
                usr=self.creds["username"],
                pwd=self.creds["password"],
                verify_ssl=self.verify_ssl,
                query="/_cat/indices/"
                + self.index_search_pattern
                + "?format=json&h=health,status,index,uuid,pri,rep,docs.count,"
                "docs.deleted,store.size,pri.store.size,creation.date.string",
            )
            for index in api.response:
                index_list.append(
                    Index(
                        cluster_name=self.custom_name,
                        _info=IndexInfo(
                            _index_types_dict=self.index_types_dict, **index
                        ),
                    )
                )
            self._index_list = index_list

        return self._index_list
