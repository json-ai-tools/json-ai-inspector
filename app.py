"""
JSON AI Inspector - A Streamlit app for JSON analysis and comparison.

This module implements the user interface using Streamlit and handles:
- Internationalization (i18n)
- Session state
- Groq AI integration
- JSON formatting and comparison

To run the application:
    $ streamlit run app.py
"""

import os
from datetime import datetime

import requests
from deepdiff import DeepDiff
from dotenv import load_dotenv
import json
import streamlit as st
from json_inspector import is_json_related, format_json, compare_json

# Cargar variables de entorno
load_dotenv()


class JSONInspectorUI:
    """Main class for the JSON Inspector user interface.

    This class handles all the user interface logic, including:
    - Internationalization (i18n)
    - Session state
    - Groq AI integration
    - JSON formatting and comparison

    The application has three main sections:
    1. Formatting: For formatting and validating JSONs
    2. AI: For asking questions about JSON using Groq
    3. Comparison: For comparing two JSONs and viewing their differences
    """

    def __init__(self):
        """Inicializar la aplicación."""
        self.setup_i18n()
        self.initialize_session_state()
        self.render_header()

    def render_header(self):
        """Renderizar el encabezado de la aplicación."""
        st.title(self.t["title"])
        st.markdown(
            '''
            <style>
                .stButton button {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                }
            </style>
            ''',
            unsafe_allow_html=True,
        )

    def setup_i18n(self):
        """Configurar internacionalización."""
        self.lang = st.sidebar.selectbox("Idioma / Language", ["Español", "English"])
        self.texts = {
            "Español": {
                "title": "JSON AI Inspector",
                "json_input": "Ingresa tu JSON",
                "format_btn": "Formatear JSON",
                "question_label": "Pregunta sobre el JSON",
                "ask_btn": "Preguntar a la IA",
                "no_api_key": "No se ha configurado la API key de Groq",
                "invalid_json": "JSON inválido",
                "json_formatted": "JSON formateado correctamente",
                "json_saved": "JSON guardado en el historial",
                "history_title": "Historial de JSON",
                "history_empty": "No hay JSON en el historial",
                "json_equal": "Los JSON son iguales",
                "json_different": "Los JSON son diferentes",
                "compare_title": "Comparar JSON",
                "json_input1": "JSON 1",
                "json_input2": "JSON 2",
                "compare_btn": "Comparar",
                "identical_jsons": "Los JSON son idénticos",
                "different_jsons": "Los JSON son diferentes",
                "donate": "Apoya el proyecto 💖",
                "limit_msg": "Has alcanzado el límite gratuito de preguntas IA.",
                "invalid_question": "❌ La pregunta no parece estar relacionada con el JSON. Reformúlala.",
            },
            "English": {
                "title": "JSON AI Inspector",
                "json_input": "Enter your JSON",
                "format_btn": "Format JSON",
                "question_label": "Question about the JSON",
                "ask_btn": "Ask AI",
                "no_api_key": "Groq API key not configured",
                "invalid_json": "Invalid JSON",
                "json_formatted": "JSON formatted successfully",
                "json_saved": "JSON saved to history",
                "history_title": "JSON History",
                "history_empty": "No JSON in history",
                "json_equal": "The JSONs are equal",
                "json_different": "The JSONs are different",
                "compare_title": "Compare JSON",
                "json_input1": "JSON 1",
                "json_input2": "JSON 2",
                "compare_btn": "Compare",
                "identical_jsons": "The JSONs are identical",
                "different_jsons": "The JSONs are different",
                "donate": "Support the project 💖",
                "limit_msg": "You have reached the free usage limit for AI questions.",
                "invalid_question": "❌ The question doesn't seem to be related to JSON. Please rephrase it.",
            },
        }
        self.t = self.texts[self.lang]

    def initialize_session_state(self):
        """Inicializar estado de la sesión."""
        if "json_history" not in st.session_state:
            st.session_state["json_history"] = []
        if "ia_uses" not in st.session_state:
            st.session_state["ia_uses"] = 0

    def render_header(self):
        """Renderizar el encabezado y botón de donación."""
        st.title(self.t["title"])
        st.markdown(
            f"""
            <center>
            <a href="https://www.paypal.com/donate/?hosted_button_id=U48Q33LRS5B9J" target="_blank">
                <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="Donate with PayPal" />
            </a>
            <p>{self.t['donate']}</p>
            </center>
            """,
            unsafe_allow_html=True,
        )

    def format_section(self):
        """Sección de formateo de JSON."""
        st.header("1. JSON")
        input_json = st.text_area(self.t["json_input"], height=200)

        if st.button(self.t["format_btn"]):
            success, result, data = format_json(input_json)
            if success:
                st.code(result, language="json")
                st.session_state["json_history"].append(
                    {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "json": data}
                )
                st.success(self.t["json_saved"])
            else:
                st.error(f"❌ Error: {result}")

    def ask_ai(self, question: str, json_data: dict) -> str:
        """Hacer una pregunta a la IA sobre el JSON.

        Args:
            question: Pregunta del usuario
            json_data: Datos JSON a analizar

        Returns:
            str: Respuesta de la IA

        Raises:
            ValueError: Si no se ha configurado la API key
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets["GROQ_API_KEY"]
            except (KeyError, AttributeError):
                raise ValueError("No se ha configurado la API key de Groq")

        if not api_key:
            raise ValueError("No se ha configurado la API key de Groq")

        prompt = f"Eres un analista JSON. Dado el siguiente JSON contesta SOLO lo relacionado a su estructura o contenido:\n\n{json_data}\n\nPregunta: {question}\n\nRespuesta concisa y específica sobre el JSON:"

        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un experto analista de datos JSON. No respondas nada que no esté relacionado directamente con el JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
            },
        )
        return res.json().get("choices", [{}])[0].get("message", {}).get("content", "Sin respuesta")

    def ai_section(self):
        """Sección de análisis con IA."""
        st.header("2. IA")
        question = st.text_input(self.t["question_label"])

        if st.button(self.t["ask_btn"]):
            if st.session_state["ia_uses"] >= 3:
                st.warning(self.t["limit_msg"])
            elif not is_json_related(question):
                st.warning(self.t["invalid_question"])
            elif st.session_state["json_history"]:
                latest = st.session_state["json_history"][-1]["json"]
                st.session_state["ia_uses"] += 1
                try:
                    response = self.ask_ai(question, latest)
                    st.write("**Respuesta:**")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error al preguntar: {e}")

    def compare_section(self):
        """Sección para comparar dos JSONs."""
        st.header(self.t["compare_title"])
        col1, col2 = st.columns(2)

        json1 = col1.text_area(self.t["json_input1"])
        json2 = col2.text_area(self.t["json_input2"])

        if st.button(self.t["compare_btn"]):
            success, error_msg, result = compare_json(json1, json2)
            if success:
                if not result["differences"]:
                    st.success(self.t["identical_jsons"])
                else:
                    st.error(self.t["different_jsons"])
                    st.json(result["differences"])
            else:
                st.error(error_msg)

    def render_history(self):
        """Renderizar historial de JSON."""
        st.sidebar.header("Historial")
        for item in st.session_state["json_history"]:
            with st.sidebar.expander(f"{item['timestamp']}"):
                st.json(item["json"])

    def format_section(self):
        """Sección para formatear JSON."""
        st.header("1. Formateo")
        json_input = st.text_area(self.t["json_input"])

        if st.button(self.t["format_btn"]):
            success, result, data = format_json(json_input)
            if success:
                st.code(result, language="json")
                st.success(self.t["json_formatted"])
                st.session_state["json_history"].append(
                    {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "json": data}
                )
                st.success(self.t["json_saved"])
            else:
                st.error(f"❌ Error: {result}")

    def run(self):
        """Ejecutar la aplicación."""
        self.format_section()
        self.ai_section()
        self.compare_section()
        self.render_history()


if __name__ == "__main__":
    app = JSONInspectorUI()
    app.run()
