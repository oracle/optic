from optic.common.api import OpenSearchAction
from optic.common.exceptions import DataError


class ClusterHealth:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Cluster:
    def __init__(
        self,
        base_url="",
        creds=None,
        verify_ssl=True,
        custom_name="",
        byte_type="gb",
    ):
        self.base_url = base_url
        self.creds = creds
        self.verify_ssl = verify_ssl

        self.custom_name = custom_name
        self.byte_type = byte_type
        self._health = None
        self._storage_percent = None

    def _calculate_storage_percent(self, disk_list) -> int:
        used = 0
        total = 0
        for disk in disk_list:
            if disk["disk.used"] is None or disk["disk.total"] is None:
                pass
            else:
                used += int(disk["disk.used"])
                total += int(disk["disk.total"])
        if total == 0:
            raise DataError(
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
