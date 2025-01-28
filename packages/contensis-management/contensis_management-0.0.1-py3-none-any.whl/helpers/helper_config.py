"""Allow access to environment variables for testing purposes."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass
class EnvConfig:
    """Access environment variables for testing purposes."""

    alias: str = field(init=False)
    username: str = field(init=False)
    password: str = field(init=False)

    def __post_init__(self):
        """Load .env file and set fields."""
        load_dotenv()
        self.alias = self._get("ALIAS")
        self.username = self._get("USERNAME")
        self.password = self._get("PASSWORD")

    def _get(self, key, default=None):
        """Prioritize environment variables over .env."""
        return os.environ.get(key) or os.getenv(key) or default


# Create a singleton instance
env_config = EnvConfig()
