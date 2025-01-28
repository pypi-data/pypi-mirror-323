"""Contensis API client module."""

import http
import logging

from contensis_management import (
    api_response_abc,
    request_handler,
    request_handler_abc,
)
from contensis_management.resource_handlers import groups, projects, users

LOGGER = logging.getLogger(__name__)


class ApiClient:
    """A class to authenticate with the Contensis API.

    It is instantiated with a RequestHandler object so that the request handler can be
    replaced during testing.
    """

    # fmt: off
    def __init__(
        self,
        alias: str = "",
        username: str = "",
        password: str = "",
        handler: request_handler_abc.RequestHandlerABC
            = request_handler.RequestHandler(),
    ):
        """Initialize the API client.

        Really the alias, username and password should be required since it doesn't make
        sense to create an instance of the API client without them.  However, making
        them optional allows the class to be instantiated in the factory methods and in
        the tests.  Potentially you could instantiate the class in a 'bad' state, but
        that that is your problem.
        """
        self.handler = handler
        self.alias = alias
        self.base_url = f"https://cms-{alias}.cloud.contensis.com"
        self.token = self._authenticate(username, password)
        self._initialize_resources()
    # fmt: on

    def _authenticate(self, username, password):
        """Authenticate with the Contensis API and return the token."""
        url = f"{self.base_url}/authenticate/connect/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "scope": (
                "openid offline_access Security_Administrator "
                "ContentType_Read ContentType_Write ContentType_Delete "
                "Entry_Read Entry_Write Entry_Delete Project_Read Project_Write "
                "Project_Delete Workflow_Administrator"
            ),
            "grant_type": "contensis_classic",
            "username": username,
            "password": password,
        }
        the_api_response = self.handler.post(url=url, headers=headers, data=data)
        if (
            the_api_response.json_data.get("error")
            or the_api_response.status_code != http.HTTPStatus.OK
        ):
            LOGGER.error("Error authenticating with the Contensis API.")
            raise PermissionError(the_api_response.json_data)
        return the_api_response.json_data["access_token"]

    def _initialize_resources(self):
        """Initialize the grouped resources with the API client."""
        self.groups = groups.Groups(self)
        self.projects = projects.Projects(self)
        self.users = users.Users(self)

    # fmt: off
    @classmethod
    def from_credentials(
        cls,
        alias: str,
        username: str,
        password: str,
        handler: request_handler_abc.RequestHandlerABC
            = request_handler.RequestHandler(),
    ):
        """Create an instance of the API client using credentials (=factory method).

        This is really just a proxy for the constructor, so not strictly necessary.
        However, I thought it was needed so there was a reciprocal for the from_token
        method.
        """
        return cls(
            alias=alias,
            username=username,
            password=password,
            handler=handler,
        )
    # fmt: on

    # fmt: off
    @classmethod
    def from_token(
        cls,
        alias: str,
        token: str,
        handler: request_handler_abc.RequestHandlerABC
            = request_handler.RequestHandler(),
    ):
        """Create an instance of the API client using a token (=factory method).

        I know this seems like hard work, but it is done this way so that using the
        credentials is the default way to create an instance of the API client.  Using
        a token is a special case mainly for working the other Contensis clients.
        """
        instance = cls.__new__(cls)  # Bypass __init__
        instance.handler = handler
        instance.alias = alias
        instance.token = token
        instance.base_url = f"https://cms-{alias}.cloud.contensis.com"
        instance._initialize_resources()
        return instance
    # fmt: on

    def get(self, url: str) -> api_response_abc.ApiResponseAbc:
        """Send a GET request to the specified URL via that provided RequestHandler."""
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}{url}"
        return self.handler.get(url=url, headers=headers)

    def head(self, url: str) -> api_response_abc.ApiResponseAbc:
        """Send a HEAD request to the specified URL via that provided RequestHandler."""
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}{url}"
        return self.handler.head(url=url, headers=headers)
