"""Group methods for the Contensis Management API."""

from typing import TYPE_CHECKING, Any, List

from contensis_management.models import group, paged_list, user

if TYPE_CHECKING:  # to avoid circular imports.
    from contensis_management import api_client


class Groups:
    """A class to handle projects in the Contensis Management API."""

    def __init__(self, the_api_client: "api_client.ApiClient"):
        """Initialize the Groups class."""
        self.client = the_api_client

    def list(self) -> paged_list.PagedList[group.Group]:
        """Get a list of the groups in the Contensis Management API."""
        the_api_response = self.client.get("/api/security/groups/")
        paged_group_list = paged_list.PagedList[group.Group]
        return paged_group_list(**the_api_response.json_data)

    def get(self, group_identifier: str) -> List[Any]:
        """Get the users in a group."""
        the_api_response = self.client.get(
            f"/api/security/groups/{group_identifier}/users"
        )
        the_user_list = the_api_response.json_data["items"]
        return [user.User(**item) for item in the_user_list]
