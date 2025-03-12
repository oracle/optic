# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/


class AliasTarget:
    def __init__(self, **kwargs):
        self.is_write_index = None
        self._set_properties_from_response(**kwargs)

    def _set_properties_from_response(self, **kwargs) -> None:
        """
        Dynamically sets attributes based off API Response dictionary

        :param dict kwargs: dictionary with response attributes
        :return: None
        :rtype: None
        """
        # TODO: Detailed Filter information
        for key, value in kwargs.items():
            if isinstance(value, str) and (value.lower() == "true" or value == "*"):
                value = True
            elif isinstance(value, str) and (value.lower() == "false" or value == "-"):
                value = False

            setattr(self, key, value)


class Alias:
    def __init__(self, alias_name=None, cluster_name=None, info_response=None):
        self.alias_name = alias_name
        self.cluster_name = cluster_name
        self.info_response = info_response
        self._targets = None
        self._write_targets = None

    @property
    def targets(self) -> list[AliasTarget]:
        """
        Provides list of AliasTarget objects associated with an alias

        :return: list of AliasTarget
        :rtype: list[AliasTarget]
        """
        if not self._targets:
            self._targets = [
                AliasTarget(**index_details) for index_details in self.info_response
            ]
        return self._targets

    @property
    def write_targets(self) -> list[AliasTarget]:
        """
        Provides list of AliasTarget objects that are write targets

        :return: list of AliasTarget
        :rtype: list[AliasTarget]
        """
        if not self._write_targets:
            self._write_targets = [
                target for target in self.targets if target.is_write_index
            ]
        return self._write_targets
