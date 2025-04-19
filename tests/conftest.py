"""Fixtures for JSON AI Inspector tests."""

import pytest


@pytest.fixture
def valid_json():
    """Return a valid JSON string."""
    return '{"name": "test", "value": 123, "nested": {"key": "value"}}'


@pytest.fixture
def invalid_json():
    """Return an invalid JSON string."""
    return '{"name": "test", value: 123}'


@pytest.fixture
def complex_json():
    """Return a complex JSON string."""
    return '''{
        "string": "hello",
        "number": 42,
        "boolean": true,
        "null": null,
        "array": [1, 2, 3],
        "object": {
            "nested": {
                "deep": "value"
            }
        }
    }'''

@pytest.fixture
def json_questions():
    """Return a list of JSON-related questions."""
    return [
        "¿Cuál es la estructura del JSON?",
        "What is the JSON structure?",
        "Qué campos tiene el JSON?",
        "What fields does the JSON have?",
        "¿Cuál es el valor del campo nested.key?"
    ]

@pytest.fixture
def mock_streamlit():
    mock = MagicMock()
    mock.session_state = {}
    mock.secrets = {}
    return mock

@pytest.fixture
def non_json_questions():
    """Return a list of non-JSON-related questions."""
    return [
        "¿Qué hora es?",
        "Hola, ¿cómo estás?",
        "Cuéntame un chiste",
        "¿Cuál es el clima hoy?"
    ]
