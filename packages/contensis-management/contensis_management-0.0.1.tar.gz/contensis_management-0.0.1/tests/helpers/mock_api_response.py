"""An implementation of the ApiResponseAbc for testing."""

from typing import Any, Dict

from contensis_management import api_response_abc


class MockApiResponse(api_response_abc.ApiResponseAbc):
    """An implementation of the ApiResponseAbc for testing."""

    def __init__(
        self,
        status_code: int,
        headers: dict | None = None,
        json_data: Dict[str, Any] | None = None,
    ):
        """Initialize the mock ApiResponse class with whatever junk it is given."""
        if headers is None:
            headers = {}
        self._status_code = status_code
        self._headers = headers
        self._json_data = json_data

    @property
    def status_code(self):
        """Return the JSON data as a string."""
        return self._status_code

    @property
    def headers(self):
        """Return the headers."""
        return self._headers

    @property
    def json_data(self):
        """Return the JSON data."""
        return self._json_data
