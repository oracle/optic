from optic.index.index_info import get_index_info


class TestIndexInfo:
    def test_get_index_info(self):
        index_name = "test_index"
        index_info = get_index_info(index_name)
        assert index_info is not None
        assert len(index_info)
        assert index_info == f"Hello OPTIC Index info for: {index_name}"
