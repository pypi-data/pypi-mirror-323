"""A paged list for when a lot of stuff is coming back from the API."""

from typing import Generic, List, TypeVar

import pydantic

from contensis_management.models import camel_case

T = TypeVar("T")  # Generic type for the items in the PagedList


class PagedList(camel_case.CamelModel, Generic[T]):
    """A paged list for when a lot of stuff is coming back from the API."""

    page_index: int = pydantic.Field(
        description="The index of the result set to return."
    )
    page_size: int = pydantic.Field(description="The number of items in the page.")
    total_count: int = pydantic.Field(
        description="The total number of items available."
    )
    page_count: int = pydantic.Field(
        description="The number of pages, based on the total_count and page_size."
    )
    items: List[T] = pydantic.Field(
        description="A container for the items being returned."
    )
