"""Confirm that the Message model works as expected."""

from contensis_management.models import message


def test_message():
    """Confirm the fields in the Message."""
    # Arrange
    status_code = 404
    detail = {
        "logId": "00000000-0000-0000-0000-000000000000",
        "message": "The specified project with ID 'website1233' does not exist",
        "data": None,
        "type": "Error",
    }
    # Act
    message_model = message.Message(status_code=status_code, detail=detail)
    # Assert
    assert message_model.status_code == status_code
    assert message_model.detail == detail


def test_message_allow_empty_detail():
    """Confirm that the Message detail can be none where we just get status code."""
    # Arrange
    status_code = 404
    # Act
    message_model = message.Message(status_code=status_code, detail=None)
    # Assert
    assert message_model.status_code == status_code
    assert message_model.detail is None
