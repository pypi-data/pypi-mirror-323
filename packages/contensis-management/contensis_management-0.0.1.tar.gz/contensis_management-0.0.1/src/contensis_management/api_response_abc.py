"""An Abstract Base Class for API responses."""

import abc
from typing import Any

from contensis_management import lower_key_dict


class ApiResponseAbc(abc.ABC):
    """An Abstract Base Class for API responses."""

    @property
    @abc.abstractmethod
    def status_code(self) -> int:
        """The status code of the response."""

    @property
    @abc.abstractmethod
    def headers(self) -> lower_key_dict.LowerKeyDict:
        """The headers of the response.

        Were are using a LowerKeyDict because the headers are case-insensitive.  In fact
        the `requests` library uses a case-insensitive dictionary for the headers.  I am
        guessing that the `httpx` library does the same thing, but have not confirmed
        it.
        """

    @property
    @abc.abstractmethod
    def json_data(self) -> Any:
        """The JSON data of the response."""
