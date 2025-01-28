"""Project methods for the Contensis Management API."""

import http
from typing import TYPE_CHECKING, Any, List

from contensis_management.models import message, project

if TYPE_CHECKING:  # to avoid circular imports.
    from contensis_management import api_client


class Projects:
    """A class to handle projects in the Contensis Management API."""

    def __init__(self, the_api_client: "api_client.ApiClient"):
        """Initialize the Projects class."""
        self.client = the_api_client

    def get(self, project_id: str) -> project.Project:
        """Get a project from the Contensis Management API."""
        the_api_response = self.client.get(f"/api/management/projects/{project_id}")
        the_project_data = the_api_response.json_data
        return project.Project(**the_project_data)

    def list(self) -> List[Any]:
        """Get a list of the projects in the Contensis Management API."""
        the_api_response = self.client.get("/api/management/projects/")
        the_project_list = the_api_response.json_data
        return [project.Project(**item) for item in the_project_list]

    def check_my_permissions(
        self, project_id: str, resource_type: str, action: str
    ) -> message.Message:
        """Check if the user is allowed to perform that action using Contensis API."""
        url = (
            f"/api/management/projects/{project_id}"
            f"/security/permissions/{resource_type}"
            f"/actions/{action}"
        )
        the_api_response = self.client.get(url=url)
        return message.Message(
            status_code=the_api_response.status_code, detail=the_api_response.json_data
        )

    def is_allowed(self, project_id: str, resource_type: str, action: str) -> bool:
        """Is the user allowed to perform that action using Contensis API."""
        the_exception = self.check_my_permissions(project_id, resource_type, action)
        return int(the_exception.status_code) == http.HTTPStatus.OK
