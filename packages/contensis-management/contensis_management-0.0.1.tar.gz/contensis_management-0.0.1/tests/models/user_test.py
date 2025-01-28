"""Confirm that the User model works as expected."""
import copy

from contensis_management.models import user

example_user = {
    "id": "00000000-0000-0000-0000-000000000000",
    "username": "admin",
    "first_name": "Admin",
    "last_name": "User",
}

def test_user():
    """Confirm the password change frequency can be a null."""
    # Arrange
    test_user = copy.deepcopy(example_user)
    test_user["credentials"] = {
        "password_change_frequency": None,
        "provider": {
            "type": "contensis",
            "name": "Contensis",
        },
    }
    # Act
    the_user = user.User(**test_user)
    # Assert
    assert the_user.credentials.password_change_frequency is None
