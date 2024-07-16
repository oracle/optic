from datetime import datetime, timezone

import dateutil.parser

from optic.cluster.cluster import Cluster
from optic.common.exceptions import OpticDataError
from optic.index.index import Index
from optic.index.index_service import (
    get_index_info,
    parse_bytes,
    parse_filters,
    parse_sort_by,
)


class TestIndexService:
    def test_get_clusters_and_groups(self):
        # TODO
        assert 1 == 1

    def test_parse_bytes(self):
        assert parse_bytes(1) == 1
        assert parse_bytes(1.0) == 1.0
        assert parse_bytes("3.0") == 3.0
        assert parse_bytes("37b") == 37
        assert parse_bytes("37754.6b") == 37754.6
        assert parse_bytes("320kb") == 320 * 2**10
        assert parse_bytes("320mb") == 320 * 2**20
        assert parse_bytes("320gb") == 320 * 2**30
        assert parse_bytes("320tb") == 320 * 2**40
        assert parse_bytes("320.75gb") == 320.75 * 2**30
        assert parse_bytes("320.754b") == 320.754
        # TODO: Import pytest for exception asserts
        try:
            parse_bytes("320.75yb")
        except OpticDataError as e:
            assert str(e) == "Unrecognized storage format: 320.75yb"
        try:
            parse_bytes("wasdf")
        except OpticDataError as e:
            assert str(e) == "Unrecognized storage format: wasdf"
        try:
            parse_bytes("waskb")
        except OpticDataError as e:
            assert str(e) == "Unrecognized storage format: waskb"
        try:
            parse_bytes("wasmb")
        except OpticDataError as e:
            assert str(e) == "Unrecognized storage format: wasmb"
        try:
            parse_bytes("wasgb")
        except OpticDataError as e:
            assert str(e) == "Unrecognized storage format: wasgb"
        try:
            parse_bytes("wastb")
        except OpticDataError as e:
            assert str(e) == "Unrecognized storage format: wastb"

    def test_get_index_info(self):
        test_cluster = Cluster(custom_name="test_cluster")
        test_cluster._index_list = []
        sim_response = {
            "health": "yellow",
            "status": "open",
            "index": "stockindex",
            "uuid": "XXX",
            "pri": "1",
            "rep": "1",
            "docs.count": "2016",
            "docs.deleted": "15",
            "store.size": "954kb",
            "pri.store.size": "954kb",
            "creation.date.string": "2024-06-04T15:17:41.806Z",
        }
        test_index_types = {"STOCK": "(.*)ocki(.*)$"}
        test_index = Index(
            cluster_name="test_cluster",
            index_types_dict=test_index_types,
            info_response=sim_response,
        )
        test_cluster._index_list.append(test_index)

        test_cluster_list = [test_cluster]

        dict_response = get_index_info(test_cluster_list[0]._index_list)
        assert dict_response[0]["name"] == "stockindex"
        assert (
            dict_response[0]["age"]
            == (
                datetime.now(timezone.utc).date()
                - dateutil.parser.isoparse(sim_response["creation.date.string"]).date()
            ).days
        )
        assert dict_response[0]["type"] == "STOCK"
        assert dict_response[0]["count"] == 2016
        assert dict_response[0]["index_size"] == "954kb"
        assert dict_response[0]["shard_size"] == "954.0kb"
        assert dict_response[0]["pri"] == 1
        assert dict_response[0]["rep"] == 1
        assert dict_response[0]["cluster"] == "test_cluster"

    def test_parse_filters(self):
        filter_dict = {
            "min_age": 3,
            "max_age": 8,
            "min_index_size": "200b",
            "max_index_size": "800kb",
            "min_shard_size": "200b",
            "max_shard_size": "800kb",
            "min_doc_count": 200,
            "max_doc_count": 500,
            "type_filter": {
                "type_1": "reg_ex_1",
                "type_2": "reg_ex_2",
                "type_3": "reg_ex_3",
            },
        }
        filter_function_list = parse_filters(filter_dict)
        index_info_dict = {
            "pri.store.size": "300kb",
            "docs.count": "600",
        }
        test_index = Index(info_response=index_info_dict)
        test_index.info._age = 10
        test_index.info._index_type = "type_1"
        test_index.info._shard_size = "150b"
        assert filter_function_list[0](test_index) is True
        assert filter_function_list[1](test_index) is False
        assert filter_function_list[2](test_index) is True
        assert filter_function_list[3](test_index) is True
        assert filter_function_list[4](test_index) is False
        assert filter_function_list[5](test_index) is True
        assert filter_function_list[6](test_index) is True
        assert filter_function_list[7](test_index) is False
        assert filter_function_list[8](test_index) is False
        assert filter_function_list[9](test_index) is True
        assert filter_function_list[10](test_index) is True

    def test_parse_sort_by(self):
        sort_list = [
            "age",
            "name",
            "index-size",
            "shard-size",
            "doc-count",
            "type",
            "primary-shards",
            "replica-shards",
        ]
        sort_function_list = parse_sort_by(sort_list)
        index_info_dict = {
            "index": "test_name",
            "pri.store.size": "300kb",
            "docs.count": "600",
            "pri": "1",
            "rep": "0",
        }
        test_index = Index(info_response=index_info_dict)
        test_index.info._age = 10
        test_index.info._index_type = "type_1"
        test_index.info._shard_size = "150b"
        assert sort_function_list[0](test_index) == 10
        assert sort_function_list[1](test_index) == "test_name"
        assert sort_function_list[2](test_index) == 300 * 2**10
        assert sort_function_list[3](test_index) == 150
        assert sort_function_list[4](test_index) == 600
        assert sort_function_list[5](test_index) == "type_1"
        assert sort_function_list[6](test_index) == 1
        assert sort_function_list[7](test_index) == 0
