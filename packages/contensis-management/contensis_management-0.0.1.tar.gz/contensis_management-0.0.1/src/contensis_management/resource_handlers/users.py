"""User methods for the Contensis Security API."""

import http
from typing import TYPE_CHECKING, Any, List

from contensis_management.models import message, user

if TYPE_CHECKING:  # to avoid circular imports.
    from contensis_management import api_client


class Users:
    """A class to handle users in the Contensis Security API."""

    def __init__(self, the_api_client: "api_client.ApiClient"):
        """Initialize the Users class."""
        self.client = the_api_client

    def get(self, user_id: str) -> user.User:
        """Get a single user from the Contensis Security API."""
        url = f"/api/security/users/{user_id}"
        the_api_response = self.client.get(url=url)
        the_user = the_api_response.json_data
        return user.User(**the_user)

    def list(self) -> List[Any]:
        """Get a list of the users from the Contensis Security API."""
        url = "/api/security/users/"
        the_api_response = self.client.get(url=url)
        the_user_list = the_api_response.json_data["items"]
        return [user.User(**item) for item in the_user_list]

    def check_user_groups(self, user_id: str, group_names: str) -> message.Message:
        """Check if the user has permission to perform the action.

        Status codes:
        204: The user is in the group.
        404: The user is not in the group.
        """
        url = f"/api/security/users/{user_id}/groups/{group_names}"
        the_api_response = self.client.head(url=url)
        return message.Message(
            status_code=the_api_response.status_code,
            detail=the_api_response.json_data or {},
        )

    def is_in_groups(self, user_id: str, group_names: str) -> bool:
        """Is the user in these groups."""
        the_exception = self.check_user_groups(user_id, group_names)
        return int(the_exception.status_code) == http.HTTPStatus.NO_CONTENT
