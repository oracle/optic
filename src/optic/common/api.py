# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

import requests
import urllib3
from requests.auth import HTTPBasicAuth

from optic.common.exceptions import OpticAPIError

urllib3.disable_warnings()


class OpenSearchAction:
    def __init__(self, base_url="", usr="", pwd=None, verify_ssl=True, query=""):
        self.base_url = base_url
        self.usr = usr
        self.pwd = pwd
        self.verify_ssl = verify_ssl
        self.query = query

        self._response = None

    @property
    def response(self) -> list | dict:
        """
        Returns JSON-like object with response data

        :return: JSON-like object with response data
        :rtype: list | dict
        """
        if not self._response:
            try:
                basic = HTTPBasicAuth(self.usr, self.pwd)
                self._response = requests.get(
                    self.base_url + self.query,
                    verify=self.verify_ssl,
                    auth=basic,
                    timeout=6,
                )
                self._response.raise_for_status()
            except requests.exceptions.RequestException as err:
                raise OpticAPIError(str(err)) from err

            self._response = self._response.json()

        return self._response
