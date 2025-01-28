"""Confirm that the SecurityListOptions model works as expected."""

from contensis_management.models import page_options, security_list_options


def test_security_list_options():
    """Confirm the fields in the SecurityListOptions."""
    # Arrange
    page_index = 0
    page_size = 5
    my_query = "query"
    my_order = "order"
    # Act

    security_list_options_model = security_list_options.SecurityListOptions(
        page_options=page_options.PageOptions(
            page_index=page_index, page_size=page_size
        ),
        query=my_query,
        order=my_order,
    )
    # Assert
    the_page_options = security_list_options_model.page_options
    assert the_page_options.page_index == 0
    assert security_list_options_model.query == my_query
    assert security_list_options_model.order == my_order
