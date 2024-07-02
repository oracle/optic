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
    def response(self) -> dict:
        if not self._response:
            basic = HTTPBasicAuth(self.usr, self.pwd)
            self._response = requests.get(
                self.base_url + self.query,
                verify=self.verify_ssl,
                auth=basic,
                timeout=3,
            )
            try:
                self._response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                raise OpticAPIError(str(err)) from err
            if (
                self._response.headers["Content-Type"]
                == "application/json; charset=UTF-8"
            ):
                return self._response.json()
            else:
                raise OpticAPIError(
                    "Unrecognized content type from call to " + self.query
                )

        return self._response
