"""
JSON AI Inspector - A Streamlit app for JSON analysis, comparison, and data generation.

This module implements the user interface using Streamlit and handles:
- Internationalization (i18n) with Spanish/English support
- Session state management and history
- Groq AI integration for JSON analysis
- JSON formatting and comparison
- CSV export for Excel compatibility
- Mock data generation with type inference
- Type definitions generation for Python/Go/TypeScript

Features:
1. JSON Formatting
   - Pretty print JSON with syntax highlighting
   - Export to CSV for Excel compatibility
   - Generate type definitions

2. AI Analysis
   - Natural language queries about JSON structure
   - Powered by Groq AI for intelligent responses

3. JSON Comparison
   - Compare two JSON structures
   - Highlight differences and changes

4. Mock Data Generation
   - Generate sample data based on JSON structure
   - Support for common data types (string, number, date, etc.)
   - Custom types like email, phone, url, objectId
   - Array support with type inference
   - History of generated datasets

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
from json_inspector import (
    is_json_related, format_json, compare_json, json_to_csv,
    generate_types, generate_mock_data
)

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
                "mock_data_input": "Estructura JSON para generar datos",
                "mock_data_records": "Cantidad de registros",
                "generate_mock_btn": "Generar datos",
                "title": "JSON AI Inspector",
                "json_input": "Ingresa tu JSON",
                "format_btn": "Formatear JSON",
                "export_csv_btn": "Exportar a CSV",
                "csv_success": "JSON exportado a CSV correctamente",
                "csv_error": "Error al exportar a CSV",
                "generate_types_btn": "Generar Tipos",
                "types_title": "Tipos Generados",
                "python_tab": "Python",
                "typescript_tab": "TypeScript",
                "golang_tab": "Golang",
                "types_error": "Error al generar tipos",
                "base_name_label": "Nombre base para los tipos",
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
                "mock_data_title": "Mock Data Generator",
                "mock_data_description": "Generate mock data based on JSON structure",
                "mock_data_example_title": "Example Structure",
                "mock_data_example_description": "Define data types using a JSON structure. Supported types: string, integer, number, boolean, date, email, phone, url, objectId, array<type>",
                "mock_data_input": "JSON structure for generating data",
                "mock_data_btn": "Generate Data",
                "mock_data_records": "Number of records",
                "mock_data_success": "Data generated successfully",
                "mock_data_error": "Error generating data",
                "mock_data_export": "Export JSON",
                "mock_data_history": "Data History",
                "mock_data_help": "Help",
                "mock_data_help_text": "Use this generator to create mock data based on a JSON structure. Define data types using a simple JSON structure.",
                "ai_assistant_title": "Asistente de IA",
                "ai_assistant_prompt": "Puedes preguntar sobre el JSON más reciente",
                "response_label": "Respuesta",
                "error_label": "Error",
                "question_placeholder": "Escribe tu pregunta para AI aquí..."
            },
            "English": {
                "mock_data_input": "Enter the JSON structure",
                "mock_data_records": "Number of records",
                "generate_mock_btn": "Generate Data",
                "title": "JSON AI Inspector",
                "json_input": "Enter your JSON",
                "format_btn": "Format JSON",
                "export_csv_btn": "Export to CSV",
                "csv_success": "JSON exported to CSV successfully",
                "csv_error": "Error exporting to CSV",
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
                "generate_types_btn": "Generate Types",
                "types_title": "Generated Types",
                "python_tab": "Python",
                "typescript_tab": "TypeScript",
                "golang_tab": "Golang",
                "types_error": "Error generating types",
                "base_name_label": "Base name for types",
                "mock_data_title": "3. Data Generation",
                "mock_data_description": "Generate dummy data based on JSON structure.",
                "mock_data_input": "Enter the JSON structure",
                "mock_data_example_title": "Example Structure",
                "mock_data_example_description": "You can use this structure as a base and modify it according to your needs. Supported types are: string, integer, number, boolean, date, email, phone, url, objectId and array<type>.",
                "num_records_label": "Number of records (max. 1000)",
                "mock_data_records": "Number of records",
                "mock_data_btn": "Generate Data",
                "mock_data_success": "Data generated successfully",
                "mock_data_error": "Error generating data",
                "mock_data_json": "Generated JSON",
                "mock_data_export": "Export JSON",
                "mock_data_history": "Generated data history",
                "ai_assistant_title": "AI Assistant",
                "ai_assistant_prompt": "You can ask about the latest JSON",
                "response_label": "Response",
                "error_label": "Error",
                "question_placeholder": "Enter your question for AI here..."
            },
        }
        self.t = self.texts[self.lang]

    def initialize_session_state(self):
        """Inicializar estado de la sesión."""
        if "json_history" not in st.session_state:
            st.session_state["json_history"] = []
        if "ia_uses" not in st.session_state:
            st.session_state["ia_uses"] = 0
        if "mock_data_history" not in st.session_state:
            st.session_state["mock_data_history"] = []

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
        """Sección para formatear JSON."""
        st.header("1. Formateo")
        # Si hay un pending_load_json, actualizar y recargar
        if "pending_load_json" in st.session_state:
            st.session_state["format_json_input"] = st.session_state["pending_load_json"]
            del st.session_state["pending_load_json"]
            st.experimental_rerun()
        json_input = st.text_area(self.t["json_input"], key="format_json_input")

        if st.button(self.t["format_btn"], key="format_btn"):
            success, result, data = format_json(json_input)
            if success:
                st.code(result, language="json")
                st.success(self.t["json_formatted"])
                st.session_state["json_history"].append(
                    {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "json": data}
                )
                st.success(self.t["json_saved"])
            else:
                st.error(f"❌ {self.t['invalid_json']}: {result}")

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
                        "content": "Eres un experto analista de datos JSON. No respondas nada que no esté relacionado directamente con el JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
        )
        return res.json().get("choices", [{}])[0].get("message", {}).get("content", "Sin respuesta")

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

    def mock_data_section(self):
        """Sección para generar datos dummy."""
        st.header(self.t["mock_data_title"])
        st.write(self.t["mock_data_description"])

        # Inicializar historial de datos generados si no existe
        if "mock_data_history" not in st.session_state:
            st.session_state["mock_data_history"] = []

        # Ejemplo de estructura JSON
        example_json = {
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

        # Mostrar ejemplo y explicación
        with st.expander("📝 " + self.t["mock_data_example_title"]):
            st.write(self.t["mock_data_example_description"])
            st.code(json.dumps(example_json, indent=2), language="json")

        # Input para el JSON y número de registros
        json_input = st.text_area(self.t["mock_data_input"], key="mock_data_input")
        num_records = st.number_input(
            self.t["mock_data_records"],
            min_value=1,
            max_value=1000,
            value=5,
            key="mock_data_records",
        )

        button_pressed = st.button(self.t["mock_data_btn"], key="mock_data_btn")
        if button_pressed:
            success, error_msg, records = generate_mock_data(json_input, num_records)
            if success:
                # Mostrar datos generados y guardar en historial
                st.success(self.t["mock_data_success"])
                st.json(records)
                st.session_state["mock_data_history"].append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "json": records
                })
                # Botón de exportación
                st.download_button(
                    label=self.t["mock_data_export"],
                    data=json.dumps(records, indent=2),
                    file_name=f"mock_data_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json",
                    mime="application/json",
                )
            else:
                st.error(f"❌ {self.t['mock_data_error']}: {error_msg}")
        # Mostrar historial solo si no se acaba de presionar el botón
        elif st.session_state["mock_data_history"]:
            st.subheader(self.t["mock_data_history"])
            for item in st.session_state["mock_data_history"]:
                with st.expander(f"📅 {item['timestamp']}"):
                    st.code(json.dumps(item['json'], indent=2), language="json")
                    st.download_button(
                        label=self.t["mock_data_export"],
                        data=json.dumps(item['json'], indent=2),
                        file_name=f"mock_data_{item['timestamp'].replace(' ', '_')}.json",
                        mime="application/json",
                    )

    def render_history(self):
        """Renderizar historial de JSON."""
        col1, col2, col3 = st.columns(3)
        json_input = st.session_state.get("format_json_input", "")

        if col2.button(self.t["export_csv_btn"], key="export_csv_btn"):
            success, error_msg, csv_data = json_to_csv(json_input)
            if success:
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_data,
                    file_name="json_export.csv",
                    mime="text/csv",
                )
                st.success(self.t["csv_success"])
            else:
                st.error(f"❌ {self.t['csv_error']}: {error_msg}")

        if col3.button(self.t["generate_types_btn"], key="generate_types_btn"):
            base_name = st.text_input(self.t["base_name_label"], value="Root", key="base_name_input")
            success, error_msg, types = generate_types(json_input, base_name)
            if success:
                st.header(self.t["types_title"])
                tabs = st.tabs([self.t["python_tab"], self.t["typescript_tab"], self.t["golang_tab"]])
                with tabs[0]:
                    st.code(types["python"], language="python")
                with tabs[1]:
                    st.code(types["typescript"], language="typescript")
                with tabs[2]:
                    st.code(types["golang"], language="go")
            else:
                st.error(f"❌ {self.t['types_error']}: {error_msg}")

        # Mostrar historial en la barra lateral
        st.sidebar.subheader(self.t["history_title"])
        json_history = st.session_state.get("json_history", [])
        if not json_history:
            st.sidebar.info(self.t["history_empty"])
        else:
            # Botón Copilot AI solo si hay historial
            ai_expander = None
            if len(json_history) > 0:
                if st.sidebar.button(self.t["ask_btn"], key="ai_copilot_btn"):
                    st.session_state["show_ai_expander"] = True
            if st.session_state.get("show_ai_expander", False):
                with st.sidebar.expander(self.t["ai_assistant_title"], expanded=True):
                    st.markdown(f"<small>{self.t['ai_assistant_prompt']}</small>", unsafe_allow_html=True)
                    latest_json = json_history[-1]["json"]
                    ai_question = st.text_input(self.t["question_label"], key="ai_sidebar_question", placeholder=self.t["question_placeholder"])
                    st.code(json.dumps(latest_json, indent=2), language="json")
                    if st.button(self.t["ask_btn"], key="ai_sidebar_ask_btn"):
                        try:
                            response = self.ask_ai(ai_question, latest_json)
                            st.markdown(f"**{self.t['response_label']}:** {response}")
                        except Exception as e:
                            st.error(f"{self.t['error_label']}: {e}")
            for idx, item in enumerate(reversed(json_history)):
                with st.sidebar.expander(f"📅 {item['timestamp']}"):
                    st.code(json.dumps(item['json'], indent=2), language="json")
                    if st.button("Cargar en editor", key=f"load_json_{idx}"):
                        st.session_state["pending_load_json"] = json.dumps(item['json'], indent=2)
                        st.experimental_rerun()

    def run(self):
        """Ejecutar la aplicación."""
        self.format_section()
        self.compare_section()
        self.mock_data_section()
        self.render_history()


if __name__ == "__main__":
    app = JSONInspectorUI()
    app.run()
