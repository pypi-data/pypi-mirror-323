"""Confirm that the PageList model works as expected."""

from contensis_management.models import paged_list


def test_page_list():
    """Confirm the fields in the PagedList."""
    # Arrange
    page_index = 0
    page_size = 5
    total_count = 13
    page_count = 3
    items = [1, 2, 3, 4, 5]
    # Act
    page_list = paged_list.PagedList[int](
        page_index=page_index,
        page_size=page_size,
        total_count=total_count,
        page_count=page_count,
        items=items,
    )
    # Assert
    assert page_list.page_index == page_index
    assert page_list.total_count == total_count
    assert page_list.page_size == page_size
    assert page_list.page_size == page_size
    assert page_list.items == items
