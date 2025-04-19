"""Tests for the JSON AI Inspector core functionality."""

import pytest
from json_inspector import is_json_related, format_json, compare_json


@pytest.mark.parametrize("question", [
    pytest.param("¿Cuál es la estructura del JSON?", id="structure"),
    pytest.param("Muestra el valor del campo nombre", id="field"),
    pytest.param("¿Qué propiedades tiene el objeto?", id="properties"),
])
def test_is_json_related_with_json_keywords(question):
    """Test that questions with JSON-related keywords return True."""
    assert is_json_related(question)


@pytest.mark.parametrize("question", [
    pytest.param("¿Qué hora es?", id="time"),
    pytest.param("Hola, ¿cómo estás?", id="greeting"),
    pytest.param("Cuéntame un chiste", id="joke"),
])
def test_is_json_related_with_non_json_keywords(question):
    """Test that questions without JSON-related keywords return False."""
    assert not is_json_related(question)


@pytest.mark.parametrize("question", [
    pytest.param("¿Cuál es la ESTRUCTURA del Json?", id="structure_caps"),
    pytest.param("muestra el VALOR del CAMPO nombre", id="field_caps"),
    pytest.param("¿Qué PROPIEDADES tiene el OBJETO?", id="properties_caps"),
])
def test_is_json_related_case_insensitive(question):
    """Test that the function is case-insensitive."""
    assert is_json_related(question)


def test_format_json_valid(valid_json):
    """Test formatting valid JSON."""
    success, formatted, data = format_json(valid_json)
    assert success
    assert '"name": "test"' in formatted
    assert data["name"] == "test"
    assert data["value"] == 123
    assert data["nested"]["key"] == "value"


def test_format_json_complex(complex_json):
    """Test formatting complex JSON with various data types."""
    success, formatted, data = format_json(complex_json)
    assert success
    assert isinstance(data["string"], str)
    assert isinstance(data["number"], int)
    assert isinstance(data["boolean"], bool)
    assert data["null"] is None
    assert isinstance(data["array"], list)
    assert isinstance(data["object"], dict)
    assert data["object"]["nested"]["deep"] == "value"


def test_format_json_invalid(invalid_json):
    """Test formatting invalid JSON."""
    success, error_msg, data = format_json(invalid_json)
    assert not success
    assert "expecting property name" in error_msg.lower()
    assert data is None


def test_format_json_empty():
    """Test formatting empty input."""
    success, error_msg, data = format_json("")
    assert not success
    assert data is None


def test_format_json_whitespace():
    """Test formatting whitespace input."""
    success, error_msg, data = format_json("   \n\t   ")
    assert not success
    assert data is None


def test_compare_json_valid(valid_json):
    """Test comparing two valid JSONs."""
    json_b = '{"name": "test", "value": 456, "nested": {"key": "different"}}'
    success, error_msg, result = compare_json(valid_json, json_b)
    assert success
    assert error_msg == ""
    assert result["differences"] is not None


def test_compare_json_identical(valid_json):
    """Test comparing identical JSONs."""
    success, error_msg, result = compare_json(valid_json, valid_json)
    assert success
    assert error_msg == ""
    assert result["differences"] is None


def test_compare_json_invalid():
    """Test comparing with invalid JSON."""
    success, error_msg, result = compare_json("{invalid", "{}")
    assert not success
    assert "json inválido" == error_msg.lower()
    assert result == {}


def test_compare_json_empty():
    """Test comparing with empty input."""
    success, error_msg, result = compare_json("", "")
    assert not success
    assert result == {}


def test_compare_json_whitespace(valid_json):
    """Test comparing with whitespace input."""
    success, error_msg, result = compare_json(valid_json, "   \n\t   ")
    assert not success
    assert result == {}
