"""Make sure that the json from the API response is accepted by the project model."""

from contensis_management.models import project

example_project_json: dict = {
    "id": "website",
    "uuid": "f06a1234-ebf2-96f5-3f85-f0612f12e6fb",
    "name": "Website",
    "description": "This is the description for the Website project..",
    "primaryLanguage": "en-GB",
    "supportedLanguages": ["en-GB", "en-NZ", "en-US", "fr-CA", "de-AT", "de-DE"],
    "color": "blue",
    "deliverySysExclusions": [],
}


def test_project_model() -> None:
    """Pass in camelCase json and confirm that the model converts it to snake_case."""
    # Arrange
    the_project = project.Project(**example_project_json)
    # Act
    # Assert
    assert the_project.id == "website"
    assert the_project.name == "Website"
    assert "This is the description" in str(the_project.description)
    assert the_project.primary_language == "en-GB"
    number_of_supported_languages = 6
    assert len(the_project.supported_languages) == number_of_supported_languages
    assert not the_project.delivery_sys_exclusions  # should be an empty list.
