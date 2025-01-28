"""The Group model."""

from contensis_management.models import camel_case


class Group(camel_case.CamelModel):
    """A Contensis group."""

    id: str
    name: str
    description: str | None = None  # sometimes the description is empty.
    custom: dict
    type: str
    user_count: int
    child_group_count: int
    auto_membership_email_domains: list | None
