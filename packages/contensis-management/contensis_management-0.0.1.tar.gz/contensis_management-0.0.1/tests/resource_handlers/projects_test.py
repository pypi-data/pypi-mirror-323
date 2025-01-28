"""Confirm that the projects resource handler works as expected."""

import http

from contensis_management import (
    api_client,
    request_handler_abc,
)
from contensis_management.resource_handlers import projects
from tests.helpers import mock_api_response

mock_projects_json: list[dict] = [
    {
        "color": "blue",
        "deliverySysExclusions": [],
        "description": "This is the description for the Website project.",
        "id": "website",
        "name": "Website",
        "primaryLanguage": "en-GB",
        "supportedLanguages": ["en-GB", "en-NZ", "en-US", "fr-CA", "de-AT", "de-DE"],
        "uuid": "f12a1234-ebf1-12f5-7f83-f0617f43e6fb",
    },
    {
        "color": "gray",
        "deliverySysExclusions": [],
        "description": "",
        "id": "testNewProject",
        "name": "test new project",
        "primaryLanguage": "en-GB",
        "supportedLanguages": ["en-GB"],
        "uuid": "f1234a89-bcda-9701-4b58-1234c634a26e",
    },
    {
        "color": "green",
        "deliverySysExclusions": [],
        "description": "",
        "id": "danMonolingual",
        "name": "Dan Monolingual",
        "primaryLanguage": "en-GB",
        "supportedLanguages": ["en-GB"],
        "uuid": "4b12345-06d1-97d8-57ef-ad12df847991",
    },
]


class MockRequestHandlerSuccessful(request_handler_abc.RequestHandlerABC):
    """A mock implementation of the RequestHandler class."""

    def post(self, url, headers=None, data=None):
        """Return a dummy token that is a plausible length."""
        return mock_api_response.MockApiResponse(
            status_code=200, json_data={"access_token": "mock_token"}
        )

    def get(self, url, headers=None):
        """Return a list of projects."""
        return mock_api_response.MockApiResponse(
            status_code=http.HTTPStatus.OK, json_data=mock_projects_json
        )

    def head(self, url, headers=None):
        """Return a list of users."""
        raise NotImplementedError("Not implemented")


def test_list_projects() -> None:
    """Test the list projects with a mock resource handler."""
    # Arrange
    mock_request_handler = MockRequestHandlerSuccessful()
    client = api_client.ApiClient(handler=mock_request_handler)
    projects_handler = projects.Projects(client)
    # Act
    the_projects = projects_handler.list()
    # Assert
    # There are three projects in the mock data.
    number_of_projects = 3
    assert len(the_projects) == number_of_projects
    # The first project is the Website project.
    assert the_projects[0].id == "website"
    assert the_projects[0].name == "Website"
    assert "This is the description" in the_projects[0].description
