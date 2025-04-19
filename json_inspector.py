"""
Core module containing the main functions for JSON AI Inspector.

This module provides functions for:
- Validating if a question is JSON-related
- Formatting JSON strings
- Comparing two JSONs and finding their differences

Example:
    >>> from json_inspector import is_json_related, format_json, compare_json
    >>> is_json_related("What is the JSON structure?")
    True
    >>> json_str = '{"name": "test"}'
    >>> formatted = format_json(json_str)
    >>> print(formatted)
    {
        "name": "test"
    }
"""

import json
from deepdiff import DeepDiff
from typing import Any, Dict, List, Optional, Tuple


def is_json_related(question: str) -> bool:
    """Check if a question is related to JSON analysis.

    Args:
        question: The question to analyze

    Returns:
        bool: True if the question appears to be JSON-related
    """
    keywords = [
        "json", "campo", "clave", "valor",
        "estructura", "propiedad", "elemento", "objeto"
    ]
    return any(word in question.lower() for word in keywords)


def format_json(json_str: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Format a JSON string and validate its structure.

    Args:
        json_str: The JSON string to format

    Returns:
        Tuple containing:
        - bool: True if formatting was successful
        - str: Formatted JSON string or error message
        - Optional[Dict]: Parsed JSON object if successful, None if failed
    """
    try:
        data = json.loads(json_str)
        formatted = json.dumps(data, indent=4, ensure_ascii=False)
        return True, formatted, data
    except Exception as e:
        return False, str(e), None


def compare_json(json_a: str, json_b: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Compare two JSON strings and return their differences.

    Args:
        json_a: Primer JSON string
        json_b: Segundo JSON string

    Returns:
        tuple[bool, str, dict]: (Éxito, mensaje de error, resultado)
    """
    try:
        json1 = json.loads(json_a)
        json2 = json.loads(json_b)

        if json1 == json2:
            return True, "", {"differences": None}

        diff = DeepDiff(json1, json2)
        return True, "", {"differences": diff.to_dict()}
    except json.JSONDecodeError:
        return False, "JSON inválido", {}
