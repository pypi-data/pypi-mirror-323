"""A project model."""

from typing import List

from contensis_management.models import camel_case


class Project(camel_case.CamelModel):
    """A Contensis project model."""

    id: str
    uuid: str
    name: str
    description: str | None = None  # sometimes the description is empty.
    primary_language: str
    supported_languages: List[str] = []
    color: str
    delivery_sys_exclusions: List[str] = []
