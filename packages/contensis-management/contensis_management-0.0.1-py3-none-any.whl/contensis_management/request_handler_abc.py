"""Abstract base class for RequestHandler classes.

This is so the RequestHandler classes can be easily swapped out for testing.
"""

from abc import ABC, abstractmethod

from contensis_management import api_response_abc


class RequestHandlerABC(ABC):
    """Abstract base class for RequestHandler classes."""

    @abstractmethod
    def get(self, url: str, headers=None) -> api_response_abc.ApiResponseAbc:
        """Send a GET request to the specified URL."""

    @abstractmethod
    def post(
        self, url: str, headers=None, data=None
    ) -> api_response_abc.ApiResponseAbc:
        """Send a POST request to the specified URL."""

    @abstractmethod
    def head(self, url: str, headers=None) -> api_response_abc.ApiResponseAbc:
        """Send a HEAD request to the specified URL."""
