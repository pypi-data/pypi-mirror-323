"""Base class for models that should be camel cased."""

import pydantic
from pydantic import alias_generators


class CamelModel(pydantic.BaseModel):
    """Ensure that the model is camel cased."""

    model_config = pydantic.ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
    )
