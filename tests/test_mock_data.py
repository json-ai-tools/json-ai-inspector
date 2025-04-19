"""Tests for the JSON AI Inspector mock data generation functionality."""

import pytest
from json_inspector import (
    analyze_json_structure,
    generate_dummy_data,
    generate_dummy_object,
    generate_mock_data
)


@pytest.fixture
def type_structure():
    """Return a sample JSON structure with type definitions."""
    return {
        "id": "objectId",
        "name": "string",
        "email": "email",
        "age": "integer",
        "score": "number",
        "active": "boolean",
        "created": "date",
        "tags": "array<string>",
        "profile": {
            "phone": "phone",
            "website": "url"
        }
    }


@pytest.fixture
def sample_data():
    """Return a sample JSON data for type inference."""
    return [
        {
            "id": "5f7b5e9b2d5a7c1234567890",
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30,
            "score": 4.5,
            "active": True,
            "created": "2025-04-19",
            "tags": ["tag1", "tag2"],
            "profile": {
                "phone": "+1234567890",
                "website": "https://example.com"
            }
        }
    ]


def test_analyze_json_structure_with_type_definitions(type_structure):
    """Test analyzing JSON structure with explicit type definitions."""
    result = analyze_json_structure(type_structure)
    assert result["id"] == "objectId"
    assert result["name"] == "string"
    assert result["email"] == "email"
    assert result["age"] == "integer"
    assert result["score"] == "number"
    assert result["active"] == "boolean"
    assert result["created"] == "date"
    assert result["tags"] == "array<string>"
    assert isinstance(result["profile"], dict)
    assert result["profile"]["phone"] == "phone"
    assert result["profile"]["website"] == "url"


def test_analyze_json_structure_with_sample_data(sample_data):
    """Test analyzing JSON structure from sample data."""
    result = analyze_json_structure(sample_data)
    assert result["id"] == "objectId"  # Based on format
    assert result["name"] == "string"
    assert result["email"] == "email"  # Based on format
    assert result["age"] == "integer"  # Based on value type
    assert result["score"] == "number"  # Based on value type
    assert result["active"] == "boolean"  # Based on value type
    assert result["created"] == "date"  # Based on format
    assert result["tags"] == "array<string>"  # Based on content
    assert isinstance(result["profile"], dict)
    assert result["profile"]["phone"] == "phone"  # Based on format
    assert result["profile"]["website"] == "url"  # Based on format


def test_generate_dummy_data_basic_types():
    """Test generating dummy data for basic types."""
    assert isinstance(generate_dummy_data("string"), str)
    assert isinstance(generate_dummy_data("integer"), int)
    assert isinstance(generate_dummy_data("number"), float)
    assert isinstance(generate_dummy_data("boolean"), bool)
    assert isinstance(generate_dummy_data("date"), str)
    assert isinstance(generate_dummy_data("array<string>"), list)


def test_generate_dummy_data_special_types():
    """Test generating dummy data for special types."""
    # ObjectId should be 24 hex characters
    assert len(generate_dummy_data("objectId")) == 24
    assert all(c in "0123456789abcdef" for c in generate_dummy_data("objectId"))

    # Email should have @ and domain
    email = generate_dummy_data("email")
    assert "@" in email
    assert "." in email.split("@")[1]

    # Phone should be a valid format
    phone = generate_dummy_data("phone")
    assert phone.startswith("+")
    assert len(phone) >= 10

    # URL should be valid
    url = generate_dummy_data("url")
    assert url.startswith("http")
    assert "." in url


def test_generate_dummy_object(type_structure):
    """Test generating a complete dummy object."""
    result = generate_dummy_object(type_structure)
    
    assert isinstance(result, dict)
    assert len(result) == len(type_structure)
    assert isinstance(result["id"], str)
    assert isinstance(result["name"], str)
    assert isinstance(result["email"], str)
    assert isinstance(result["age"], int)
    assert isinstance(result["score"], float)
    assert isinstance(result["active"], bool)
    assert isinstance(result["created"], str)
    assert isinstance(result["tags"], list)
    assert isinstance(result["profile"], dict)
    assert isinstance(result["profile"]["phone"], str)
    assert isinstance(result["profile"]["website"], str)


def test_generate_mock_data_invalid_input():
    """Test generating mock data with invalid input."""
    # Invalid JSON
    success, error, data = generate_mock_data("{invalid json}", 5)
    assert not success
    assert "JSON inválido" in error
    assert data is None

    # Empty input
    success, error, data = generate_mock_data("", 5)
    assert not success
    assert error
    assert data is None

    # Invalid number of records
    success, error, data = generate_mock_data("{}", 1001)
    assert not success
    assert "máximo" in error.lower()
    assert data is None


def test_generate_mock_data_valid_input(type_structure):
    """Test generating mock data with valid input."""
    num_records = 5
    success, error, data = generate_mock_data(type_structure, num_records)
    
    assert success
    assert not error
    assert isinstance(data, list)
    assert len(data) == num_records
    
    for record in data:
        assert isinstance(record["id"], str)
        assert isinstance(record["name"], str)
        assert isinstance(record["email"], str)
        assert isinstance(record["age"], int)
        assert isinstance(record["score"], float)
        assert isinstance(record["active"], bool)
        assert isinstance(record["created"], str)
        assert isinstance(record["tags"], list)
        assert isinstance(record["profile"], dict)
        assert isinstance(record["profile"]["phone"], str)
        assert isinstance(record["profile"]["website"], str)
