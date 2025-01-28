"""Module for PageOptions model."""

from pydantic import Field

from contensis_management.models import camel_case


class PageOptions(camel_case.CamelModel):
    """Options for a paged list."""

    page_index: int = Field(0, description="The index of the item set to return.")
    page_size: int = Field(20, description="The number of items to return.")
