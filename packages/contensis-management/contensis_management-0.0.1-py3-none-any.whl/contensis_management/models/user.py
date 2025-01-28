"""A user model."""

from datetime import datetime

from contensis_management.models import camel_case


class Provider(camel_case.CamelModel):
    """A Contensis user credential provider model."""

    type: str
    name: str


class Credentials(camel_case.CamelModel):
    """A Contensis user credentials model."""

    password_change_frequency: int | None = None
    provider: Provider


class Status(camel_case.CamelModel):
    """A Contensis user status model."""

    suspended: bool
    locked: bool
    password_reset_required: bool


class User(camel_case.CamelModel):
    """A Contensis user model."""

    id: str
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    timezone: str | None = None
    language: str | None = None
    custom: dict = {}
    credentials: Credentials | None = None
    status: Status | None = None
    created: datetime | None = None
    last_login: datetime | None = None
    last_failed_login: datetime | None = None
    modified: datetime | None = None
    expiry: datetime | None = None
    password_changed: datetime | None = None
    opt_out_of_notifications: bool | None = None
    failed_login_attempts: int | None = None
    failed_login_attempts_since_last_success: int | None = None
    successful_login_attempts: int | None = None
