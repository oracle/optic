# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

from optic.alias.alias import Alias
from optic.common.api import OpenSearchAction
from optic.common.exceptions import OpticDataError
from optic.index.index import Index


def configure_cluster(cluster, settings):
    """
    If there is a attribute in the OpticSettings object that matches an attribute
    in the Cluster object, and the value for that attribute is not None, set the attribute
    on the Cluster object to the corresponding value in the OpticSettings object

    """
    for setting, value in settings.items():
        if hasattr(cluster, setting) and value:
            setattr(cluster, setting, value)
    return cluster


class ClusterHealth:
    def __init__(self, **kwargs):
        self._set_properties_from_response(**kwargs)

    def _set_properties_from_response(self, **kwargs) -> None:
        """
        Dynamically sets attributes based off API Response dictionary

        :param dict kwargs: dictionary with response attributes
        :return: None
        :rtype: None
        """
        for key, value in kwargs.items():
            if isinstance(value, str) and value.isdigit():
                value = int(value)
            setattr(self, key, value)


class Cluster:
    def __init__(
        self,
        url=None,
        auth=None,
        verify_ssl=True,
        name=None,
        byte_type=None,  # remove this?
        search_pattern=None,
        index_type_patterns=None,
    ):
        self.url = url
        self.auth = auth
        self.verify_ssl = verify_ssl
        self.name = name
        self.byte_type = byte_type
        self.search_pattern = search_pattern or "*"
        self.index_type_patterns = index_type_patterns or {}

        self._health = None
        self._storage_percent = None
        self._index_list = None
        self._alias_list = None

    def _calculate_storage_percent(self, disk_list) -> int:
        """
        Calculate the storage percentage of cluster in use

        :param list disk_list: list of dictionaries of cluster disk information
        :return: storage percentage (0-100)
        :rtype: int
        :raises OpticDataError: if storage total is 0 or null
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
                f"Error in [{self.name}] disk capacity calculation"
                "(Total disk capacity is 0 or null)"
            )
        return int(round(100 * (float(used) / float(total))))

    @property
    def health(self) -> ClusterHealth:
        """
        Constructs and returns Cluster Health object from API call

        :return: Cluster Health object
        :rtype: ClusterHealth
        """
        if not self._health:
            print("Getting cluster health for", self.name)
            api = OpenSearchAction(
                url=self.url,
                usr=self.auth["username"],
                pwd=self.auth["password"],
                verify_ssl=self.verify_ssl,
                query="/_cluster/health?pretty",
            )
            self._health = ClusterHealth(**api.response)

        return self._health

    @property
    def storage_percent(self) -> int:
        """
        Returns the storage percentage of cluster in use from API call

        :return: storage percentage (0%-100%)
        :rtype: int
        """
        if not self._storage_percent:
            print("Getting storage percent for", self.name)
            api = OpenSearchAction(
                url=self.url,
                usr=self.auth["username"],
                pwd=self.auth["password"],
                verify_ssl=self.verify_ssl,
                query="/_cat/allocation?h=disk.used,disk.total&format=json&bytes=mb",
            )
            self._storage_percent = self._calculate_storage_percent(api.response)

        return self._storage_percent

    @property
    def index_list(self) -> list:
        """
        Returns list of Index objects associated with cluster

        :return: list of Index objects
        :rtype: list
        """
        if not self._index_list:
            index_list = []
            api = OpenSearchAction(
                url=self.url,
                usr=self.auth["username"],
                pwd=self.auth["password"],
                verify_ssl=self.verify_ssl,
                query="/_cat/indices/"
                + self.search_pattern
                + "?format=json&h=health,status,index,uuid,pri,rep,docs.count,"
                "docs.deleted,store.size,pri.store.size,creation.date.string",
            )

            # Create map for index -> write_target_alias?
            index_to_write_target = {}
            aliases = self.alias_list
            for alias in aliases:
                for write_target in alias.write_targets:
                    index_to_write_target[write_target.index] = True

            print("Getting cluster index list for", self.name)
            for index_info in api.response:
                index_list.append(
                    Index(
                        cluster_name=self.name,
                        index_name=index_info["index"],
                        write_alias=index_to_write_target.get(
                            index_info["index"], False
                        ),
                        index_type_patterns=self.index_type_patterns,
                        info_response=index_info,
                    )
                )
            self._index_list = index_list

        return self._index_list

    @property
    def alias_list(self) -> list:
        """
        Returns list of Alias objects associated with cluster

        :return: list of Alias objects
        :rtype: list
        """
        if not self._alias_list:
            alias_list = []
            api = OpenSearchAction(
                url=self.url,
                usr=self.auth["username"],
                pwd=self.auth["password"],
                verify_ssl=self.verify_ssl,
                query="/_cat/aliases/" + self.search_pattern + "?format=json",
            )

            """
            Parse multiple responses that correspond to one alias

            Response:
            [  {
                "alias": "alias1",
                "index": "stockindex",
                "filter": "-",
                "routing.index": "-",
                "routing.search": "-",
                "is_write_index": "-"
              },
              {
                "alias": "alias1",
                "index": "students",
                "filter": "*",
                "routing.index": "1",
                "routing.search": "1",
                "is_write_index": "true"
              }
            ]

            ---------------BECOMES------------------

            alias_to_indices:
            {
              "alias1" : [
                  {
                      "index": "stockindex",
                      "filter": "-",
                      "routing.index": "-",
                      "routing.search": "-",
                      "is_write_index": "-"
                  },
                  {
                      "index": "students",
                      "filter": "*",
                      "routing.index": "1",
                      "routing.search": "1",
                      "is_write_index": "true"
                  }
              ]
            }
            """

            print("Getting cluster alias list for", self.name)
            alias_to_indices = {}
            for alias_info in api.response:
                if alias_info["alias"] not in alias_to_indices.keys():
                    alias_to_indices[alias_info["alias"]] = []
                alias_to_indices[alias_info["alias"]].append(
                    {key: val for key, val in alias_info.items() if key != "alias"}
                )

            for alias_name, alias_info in alias_to_indices.items():
                alias_list.append(
                    Alias(
                        alias_name=alias_name,
                        cluster_name=self.name,
                        info_response=alias_info,
                    )
                )
            self._alias_list = alias_list

        return self._alias_list
