"""Confirm that the users resource handler works as expected."""

import http

from contensis_management import (
    api_client,
    request_handler_abc,
)
from contensis_management.resource_handlers import users
from tests.helpers import mock_api_response

mock_users_json: list[dict] = [
    {
        "created": "2024-09-03T09:51:20.113Z",
        "credentials": {
            "passwordChangeFrequency": 180,
            "provider": {"name": "contensis", "type": "contensis"},
        },
        "custom": {},
        "email": "alice@zengenti.com",
        "expiry": "2029-09-03T09:51:20.113",
        "failedLoginAttempts": 0,
        "failedLoginAttemptsSinceLastSuccess": 0,
        "firstName": "Alice",
        "id": "209e4053-f71b-45a9-ba87-3f5595caaeee",
        "language": "en-GB",
        "lastFailedLogin": None,
        "lastLogin": None,
        "lastName": "Wonderland",
        "modified": "2024-09-03T09:51:20.113Z",
        "optOutOfNotifications": False,
        "passwordChanged": "2024-09-03T09:51:20.113Z",
        "status": {"locked": False, "passwordResetRequired": False, "suspended": False},
        "successfulLoginAttempts": 0,
        "timezone": "Etc/UTC",
        "username": "user-alice",
    },
    {
        "created": "2024-09-02T12:11:49.46Z",
        "credentials": {
            "passwordChangeFrequency": 180,
            "provider": {"name": "contensis", "type": "contensis"},
        },
        "custom": {},
        "email": "bob@zengenti.com",
        "expiry": "2029-09-02T12:11:49.46",
        "failedLoginAttempts": 0,
        "failedLoginAttemptsSinceLastSuccess": 0,
        "firstName": "Bob",
        "id": "6ec2d6d8-0947-4322-ba08-5624a8206a00",
        "language": "en-GB",
        "lastFailedLogin": None,
        "lastLogin": None,
        "lastName": "Builder",
        "modified": "2024-09-02T12:11:49.46Z",
        "optOutOfNotifications": False,
        "passwordChanged": "2024-09-02T12:11:49.46Z",
        "status": {"locked": False, "passwordResetRequired": False, "suspended": False},
        "successfulLoginAttempts": 0,
        "timezone": "Etc/UTC",
        "username": "user-bob",
    },
    {
        "created": "2024-07-15T13:47:45.373Z",
        "credentials": {
            "passwordChangeFrequency": 0,
            "provider": {"name": "contensis", "type": "contensis"},
        },
        "custom": {
            "defaultView": "dashboard",
            "earlyAccess_websiteUptimeReporting": "no",
            "relationshipStatus": "0",
        },
        "email": "carol@zengenti.com",
        "expiry": None,
        "failedLoginAttempts": 0,
        "failedLoginAttemptsSinceLastSuccess": 0,
        "firstName": "Carol",
        "id": "7bdd3065-a4c3-4b61-8154-43ebc266f4ec",
        "language": "en-GB",
        "lastFailedLogin": None,
        "lastLogin": "2024-09-11T08:48:14.443Z",
        "lastName": "Christmas",
        "modified": "2024-07-15T13:47:45.373Z",
        "optOutOfNotifications": False,
        "passwordChanged": None,
        "status": {"locked": False, "passwordResetRequired": False, "suspended": False},
        "successfulLoginAttempts": 0,
        "timezone": "Europe/Paris",
        "username": "user-carol",
    },
]

mock_paged_users_json: dict = {
    "items": mock_users_json,
    "pageCount": 1,
    "pageIndex": 0,
    "pageSize": 25,
    "totalCount": 3,
}


class MockRequestHandlerAllUsers(request_handler_abc.RequestHandlerABC):
    """A mock implementation of the RequestHandler class."""

    def post(self, url, headers=None, data=None):
        """Return a dummy token when we authenticate."""
        return mock_api_response.MockApiResponse(
            status_code=200, json_data={"access_token": "mock_token"}
        )

    def get(self, url, headers=None):
        """Return a list of users."""
        return mock_api_response.MockApiResponse(
            json_data=mock_paged_users_json, status_code=http.HTTPStatus.OK
        )

    def head(self, url, headers=None):
        """Return a list of users."""
        raise NotImplementedError("Not implemented")


def test_list_users() -> None:
    """Test the list users with a mock resource handler."""
    # Arrange
    mock_request_handler = MockRequestHandlerAllUsers()
    client = api_client.ApiClient(handler=mock_request_handler)
    users_handler = users.Users(client)
    # Act
    the_users = users_handler.list()
    # Assert
    the_number_of_users = 3
    assert len(the_users) == the_number_of_users


class MockRequestHandlerOneUser(request_handler_abc.RequestHandlerABC):
    """A mock implementation of the RequestHandler class."""

    def post(self, url, headers=None, data=None):
        """Return a dummy token when we need to authenticate."""
        return mock_api_response.MockApiResponse(
            status_code=200, json_data={"access_token": "mock_token"}
        )

    def get(self, url, headers=None):
        """Return a one user."""
        return mock_api_response.MockApiResponse(
            json_data=mock_users_json[0], status_code=http.HTTPStatus.OK
        )

    def head(self, url, headers=None):
        """Return a list of users."""
        raise NotImplementedError("Not implemented")


def test_get_user() -> None:
    """Test the get user with a mock resource handler."""
    # Arrange
    mock_request_handler = MockRequestHandlerOneUser()
    client = api_client.ApiClient(handler=mock_request_handler)
    users_handler = users.Users(client)
    # Act
    the_user = users_handler.get(user_id="209e4053-f71b-45a9-ba87-3f5595caaeee")
    # Assert
    assert the_user.username == "user-alice"
    assert the_user.first_name == "Alice"
    assert the_user.last_name == "Wonderland"
