# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

import logging

import requests
import urllib3
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util.retry import Retry

from optic.common.exceptions import OpticAPIError

logging.basicConfig(level=logging.INFO)

urllib3.disable_warnings()


class OpenSearchAction:
    def __init__(
        self,
        url="",
        query="",
        retries=3,
        backoff_factor=2,
        status_forcelist=(500, 502, 503, 504),
        usr=None,
        pwd=None,
        verify_ssl=True,
    ):
        """
        Wraps the methods required to execute REST calls against the OpenSearch API.
        Args:
            url (str): The URL to send the request to
            query (str): additional string added to the end of url
            retries (int): Maximum number of retries
            backoff_factor (float): Backoff factor to apply between retries in seconds
            status_forcelist (tuple): HTTP status codes to retry on
            usr (str): username to be used in BasicAuth header
            pwd (str): password to be used in BasicAuth header
            verify_ssl (boolean): set SSL verification mode

        """

        self.url = url
        self.query = query
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist
        self.usr = (
            usr or str()
        )  # Requests 3.0.0 will no longer support None as a username
        self.pwd = (
            pwd or str()
        )  # Requests 3.0.0 will no longer support None as a password
        self.verify_ssl = verify_ssl
        self._response = None

    @property
    def response(self) -> list | dict:
        """
        Returns JSON-like object with response data

        :return: JSON-like object with response data
        :rtype: list | dict
        """

        if not self._response:
            url = self.url + self.query
            logging.debug(
                f"creating REST request to {url} with "
                f"{self.retries} retries, backoff {self.backoff_factor}, and ssl verify {self.verify_ssl}"
            )
            basic_auth = HTTPBasicAuth(self.usr, self.pwd)
            retry_strategy = Retry(
                total=self.retries,
                backoff_factor=self.backoff_factor,
                status_forcelist=self.status_forcelist,
            )
            session = requests.Session()
            session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
            session.mount("http://", HTTPAdapter(max_retries=retry_strategy))

            try:
                self._response = session.get(
                    url,
                    verify=self.verify_ssl,
                    auth=basic_auth,
                    timeout=6,
                )
                self._response.raise_for_status()
            except requests.exceptions.RequestException as err:
                # Check if retries were exhausted
                if err.args and isinstance(
                    err.args[0], urllib3.exceptions.MaxRetryError
                ):
                    raise OpticAPIError(
                        f"Request failed after {self.retries} retries {err}"
                    ) from err
                else:
                    raise OpticAPIError(
                        f"did not attempt to retry error: {err}"
                    ) from err

            self._response = self._response.json()

        return self._response
