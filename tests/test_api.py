from io import BytesIO
from unittest.mock import patch

import pytest
from urllib3.response import HTTPResponse

from optic.common.api import OpenSearchAction
from optic.common.exceptions import OpticAPIError


class TestOpenSearchActionClass:
    def _http_response(self, status: int, body_bytes: bytes):
        """
        Create a mock HTTPResponse that works with requests/urllib3 streaming.
        """
        return HTTPResponse(
            body=BytesIO(body_bytes), status=status, preload_content=False
        )

    def test_successful_request(self, mocker):
        """
        When OpenSearchAction receives a valid response, and a status code of 200, it should not raise an Exception
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"request": "valid"}

        api = OpenSearchAction(url="http://example.com/optic")
        mocker.patch("requests.Session.get", return_value=mock_response)

        assert api.response == {"request": "valid"}

    # attempt 4 different backoff_factors to ensure the number is being correctly handled by OpenSearchAction
    @pytest.mark.parametrize("backoff_factor", [0.5, 1, 2, 5])
    def test_retry_failure_until_success(self, backoff_factor):
        """
        verify that failed OpenSearchAction HTTP requests are retried, and that
        after the initial immediate retry, the requests.Session module honors the
        configurable backoff method to delay subsequent retries for the expected number
        of seconds
        """

        # make 4 total requests, 3 that should trigger a retry, and then the final request should simulate a success
        requests = [
            self._http_response(502, b'{"error":"cant get through this gateway"}'),
            self._http_response(500, b'{"error":"i am internalizing this error"}'),
            self._http_response(503, b'{"error":"this service is unavailable!"}'),
            self._http_response(200, b'{"result":"finally! a success"}'),
        ]

        # store how many seconds each retry requested the time.sleep method to wait
        requested_sleep_seconds = []

        def _patched_sleep(seconds):
            requested_sleep_seconds.append(seconds)

        with (
            patch(
                "urllib3.connectionpool.HTTPConnectionPool._make_request",
                side_effect=requests,
            ),
            patch("time.sleep", side_effect=_patched_sleep),
        ):
            action = OpenSearchAction(
                url="http://example.com/optic",
                retries=5,
                backoff_factor=backoff_factor,
            )
            result = action.response

        # Assert final response
        assert result == {"result": "finally! a success"}

        # Exponential backoff: backoff_factor * (2 ** retry_number)
        # first retry does not request a sleep before retrying
        # last request is successful
        expected_sleep_seconds = [
            backoff_factor * (2**i) for i in range(1, len(requests) - 1)
        ]
        assert requested_sleep_seconds == expected_sleep_seconds

    # attempt 4 different values for retries to ensure the number is being correctly handled by OpenSearchAction
    @pytest.mark.parametrize("retries", [4, 14, 28, 36])
    def test_retry_failure_until_exhausted(self, retries):
        """
        verify that failed OpenSearchAction HTTP requests are retried, and that
        a OpticAPIError exception is raised after exhausting the maximum number of retries
        """

        # in this test, we do not want to wait for the time.sleep method to pause execution
        def _patched_sleep(seconds):
            pass

        # make as many failed responses as needed in order to exhaust the retry count
        # first attempt is not considered a retry
        requests = [
            self._http_response(502, b'{"error":"cant get through this gateway"}')
            for _ in range(retries + 1)
        ]

        with (
            patch(
                "urllib3.connectionpool.HTTPConnectionPool._make_request",
                side_effect=requests,
            ) as mock_make_request,
            patch("time.sleep", side_effect=_patched_sleep),
        ):

            with pytest.raises(OpticAPIError) as exc_info:
                action = OpenSearchAction(
                    url="http://example.com/optic",
                    retries=retries,  # force exhaustion
                )
                _ = (
                    action.response
                )  # response is a property, so it needs to be accessed to execute

        # Assert type
        assert isinstance(exc_info.value, OpticAPIError)

        # Assert retry count shows up in message
        assert f"after {retries} retries" in str(exc_info.value)

        # Assert the root cause text is included
        assert "502 error responses" in str(exc_info.value)

        # Assert the _make_request method was called the expected number of times (first call is not considered a retry)
        assert mock_make_request.call_count == retries + 1
