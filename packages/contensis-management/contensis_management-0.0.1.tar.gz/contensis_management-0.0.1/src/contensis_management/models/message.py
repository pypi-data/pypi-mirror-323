"""A Contensis message from a resource handler."""

from contensis_management.models import camel_case


class Message(camel_case.CamelModel):
    """A Contensis style message from the endpoint."""

    status_code: int
    detail: dict | None = {}
