"""A standard response object for API requests.

I had hoped to avoid a dependency on the `requests` library in the `api_response`
module. It is easier to deal with the requests object here and I am trying to keep the
request handler and simple as possible so it is legitimate to mock it during tests.
Also it seems like the `httpx.Response` looks very similar to the `requests.Response`.
So not so bad maybe.
"""

import httpx
import requests

from contensis_management import api_response_abc, lower_key_dict


class ApiResponse(api_response_abc.ApiResponseAbc):
    """A standard response object for API requests.

    This is designed so that it can be easily mocked in tests.  Either pass in a
    `requests.Response` object or pass in the status_code, headers, and json_data.
    """

    def __init__(self, api_response: httpx.Response | requests.Response):
        """Initialize the ApiResponse from a `requests` response."""
        self._status_code = api_response.status_code
        self._headers = lower_key_dict.to_lower_key_dict(api_response.headers)
        self._json_data = self._extract_json(api_response)

    def _extract_json(self, api_response: httpx.Response | requests.Response):
        """Extract the JSON data from the API response."""
        content_type_header = self._headers.get("content-type", "")
        if api_response.content and "application/json" in content_type_header:
            return api_response.json()
        return None

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
