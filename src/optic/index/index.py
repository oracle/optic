import re
from datetime import datetime, timezone

import dateutil.parser

from optic.common.exceptions import OpticDataError


class IndexInfo:
    def __init__(self, index_types_dict=None, **kwargs):
        self.index = None
        self.pri = None
        self._age = None
        self._shard_size = None
        self._index_type = None
        self.index_types_dict = index_types_dict
        self._set_properties_from_response(**kwargs)

    def _set_properties_from_response(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, str) and value.isdigit():
                value = int(value)
            setattr(self, key, value)

    def _calculate_age(self) -> int:
        """
        Calculate the age of the index in days
        :return: age in days
        :rtype: int
        """
        return (
            datetime.now(timezone.utc).date()
            - dateutil.parser.isoparse(getattr(self, "creation.date.string")).date()
        ).days

    def _calculate_type(self) -> str:
        """
        Calculate the type of the index
        :return: index type string
        :rtype: str
        """
        for type_name, reg_ex in self.index_types_dict.items():
            if re.match(reg_ex, self.index):
                return type_name
        return "UNDEFINED"

    @property
    def age(self):
        if not self._age:
            self._age = self._calculate_age()

        return self._age

    @property
    def index_type(self):
        if not self._index_type:
            self._index_type = self._calculate_type()

        return self._index_type

    @property
    def shard_size(self):
        if not self._shard_size:
            store_size = getattr(self, "pri.store.size")
            if store_size[-1].lower() == "b":
                match store_size[-2].lower():
                    case "k":
                        self._shard_size = (
                            str(float(store_size[:-2]) / float(self.pri)) + "kb"
                        )
                    case "m":
                        self._shard_size = (
                            str(float(store_size[:-2]) / float(self.pri)) + "mb"
                        )
                    case "g":
                        self._shard_size = (
                            str(float(store_size[:-2]) / float(self.pri)) + "gb"
                        )
                    case "t":
                        self._shard_size = (
                            str(float(store_size[:-2]) / float(self.pri)) + "tb"
                        )
                    case _:
                        if store_size[-2].isnumeric():
                            self._shard_size = (
                                str(float(store_size[:-1]) / float(self.pri)) + "b"
                            )
                        else:
                            raise OpticDataError(
                                "Unrecognized index size storage format: "
                                + store_size
                                + " for index "
                                + self.index
                            )
            else:
                raise OpticDataError(
                    "Unrecognized index size storage format: "
                    + store_size
                    + " for index "
                    + self.index
                )
        return self._shard_size


class Index:
    def __init__(self, cluster_name=None, index_types_dict=None, info_response=None):
        self.cluster_name = cluster_name
        self.index_types_dict = index_types_dict
        self.info_response = info_response
        self._info = None

    @property
    def info(self) -> IndexInfo:
        if not self._info:
            self._info = IndexInfo(
                index_types_dict=self.index_types_dict, **self.info_response
            )
        return self._info
