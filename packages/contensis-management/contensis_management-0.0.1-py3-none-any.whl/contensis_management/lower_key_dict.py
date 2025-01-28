"""A dictionary that stores keys in lowercase."""

from typing import Any


class LowerKeyDict(dict):
    """A dictionary that stores keys in lowercase."""

    def __setitem__(self, key, value):
        """Set the key to lowercase."""
        super().__setitem__(key.casefold(), value)

    def __getitem__(self, key):
        """Get the value for the key in lowercase."""
        return super().__getitem__(key.casefold())


def to_lower_key_dict(original_dict: Any) -> LowerKeyDict:
    """Convert a dictionary to a LowerKeyDict."""
    lower_key_dict = LowerKeyDict()
    for key, value in original_dict.items():
        if isinstance(value, dict):
            # Recursively convert nested dictionaries
            lower_key_dict[key] = to_lower_key_dict(value)
        else:
            lower_key_dict[key] = value
    return lower_key_dict
