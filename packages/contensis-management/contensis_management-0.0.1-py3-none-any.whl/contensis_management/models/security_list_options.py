"""Options for listing groups."""

from contensis_management.models import camel_case
from contensis_management.models import page_options as page_options_model


class SecurityListOptions(camel_case.CamelModel):
    """Options for listing groups."""

    page_options: page_options_model.PageOptions
    query: str
    order: str
