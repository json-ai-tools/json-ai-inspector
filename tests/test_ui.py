"""Tests for the JSON AI Inspector UI."""

import pytest
import sys
from unittest.mock import patch, MagicMock

# Mock streamlit before importing app
sys.modules['streamlit'] = MagicMock()

# Now we can safely import our app
from app import JSONInspectorUI


@pytest.fixture
def mock_streamlit():
    """Mock all required Streamlit components."""
    with patch("streamlit.sidebar") as mock_sidebar, \
         patch("streamlit.title") as mock_title, \
         patch("streamlit.markdown") as mock_markdown, \
         patch("streamlit.session_state", new_callable=dict) as mock_state:
        mock_sidebar.selectbox.return_value = "Español"
        yield {
            "sidebar": mock_sidebar,
            "title": mock_title,
            "markdown": mock_markdown,
            "session_state": mock_state
        }


@pytest.fixture
def ui(mock_streamlit):
    """Return a JSONInspectorUI instance with mocked Streamlit."""
    return JSONInspectorUI()


def test_i18n_setup(ui):
    """Test that internationalization is properly set up."""
    assert "Español" in ui.texts
    assert "English" in ui.texts
    assert all(
        key in ui.texts["Español"]
        for key in ["title", "json_input", "format_btn", "question_label"]
    )
    assert all(
        key in ui.texts["English"]
        for key in ["title", "json_input", "format_btn", "question_label"]
    )


@pytest.mark.parametrize("lang", ["Español", "English"])
def test_language_switch(mock_streamlit, lang):
    """Test that language switching works."""
    mock_streamlit["sidebar"].selectbox.return_value = lang
    ui = JSONInspectorUI()
    assert ui.lang == lang
    assert ui.t == ui.texts[lang]


def test_initialize_session_state(ui):
    """Test that session state is properly initialized."""
    with patch('streamlit.session_state', {}) as mock_state:
        ui.initialize_session_state()
        assert "json_history" in mock_state
        assert "ia_uses" in mock_state
        assert isinstance(mock_state["json_history"], list)
        assert mock_state["ia_uses"] == 0


def test_ask_ai_without_api_key(ui):
    """Test that ask_ai raises an error when API key is not configured."""
    with patch.dict("os.environ", {}, clear=True), \
         patch("streamlit.secrets", {}):
        with pytest.raises(ValueError) as exc_info:
            ui.ask_ai("test question", {"test": "data"})
        assert "API key" in str(exc_info.value)


@patch.dict("os.environ", {"GROQ_API_KEY": "test_key"})
def test_ask_ai_with_api_key(ui):
    """Test that ask_ai makes the correct API call when API key is configured."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}]
    }

    with patch("requests.post", return_value=mock_response) as mock_post:
        response = ui.ask_ai("test question", {"test": "data"})
        
        assert response == "Test response"
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0] == "https://api.groq.com/openai/v1/chat/completions"
        assert "Bearer test_key" in mock_post.call_args[1]["headers"]["Authorization"]


def test_format_section_with_valid_json(ui, valid_json):
    """Test JSON formatting section with valid input."""
    with patch("streamlit.header"), \
         patch("streamlit.text_area", return_value=valid_json), \
         patch("streamlit.button", return_value=True), \
         patch("streamlit.code") as mock_code, \
         patch("streamlit.success") as mock_success, \
         patch("streamlit.session_state", new_callable=dict) as mock_state:
        
        mock_state["json_history"] = []
        ui.format_section()
        
        mock_code.assert_called_once()
        assert mock_success.call_count == 2  # Se llama dos veces: una para el formato y otra para el guardado
        assert len(mock_state["json_history"]) == 1


def test_format_section_with_invalid_json(ui, invalid_json):
    """Test JSON formatting section with invalid input."""
    with patch("streamlit.header"), \
         patch("streamlit.text_area", return_value=invalid_json), \
         patch("streamlit.button", return_value=True), \
         patch("streamlit.error") as mock_error:
        
        ui.format_section()
        mock_error.assert_called_once()


def test_compare_section_with_equal_jsons(ui, valid_json):
    """Test JSON comparison section with equal inputs."""
    with patch("streamlit.header"), \
         patch("streamlit.columns") as mock_columns, \
         patch("streamlit.button", return_value=True), \
         patch("streamlit.success") as mock_success, \
         patch("streamlit.json") as mock_json:
        
        col1, col2 = MagicMock(), MagicMock()
        col1.text_area.return_value = valid_json
        col2.text_area.return_value = valid_json
        mock_columns.return_value = [col1, col2]
        
        ui.compare_section()
        mock_success.assert_called_once()
        mock_json.assert_not_called()


def test_compare_section_with_different_jsons(ui, valid_json, complex_json):
    """Test JSON comparison section with different inputs."""
    with patch("streamlit.header"), \
         patch("streamlit.columns") as mock_columns, \
         patch("streamlit.button", return_value=True), \
         patch("streamlit.error") as mock_error, \
         patch("streamlit.json") as mock_json, \
         patch("streamlit.session_state", new_callable=dict) as mock_state:
        
        mock_state["json_history"] = []
        col1, col2 = MagicMock(), MagicMock()
        col1.text_area.return_value = valid_json
        col2.text_area.return_value = complex_json
        mock_columns.return_value = [col1, col2]
        
        ui.compare_section()
        mock_error.assert_called_once()
        mock_json.assert_called_once()
