# 🧠 JSON AI Inspector

[English](#english) | [Español](#español)

<a name="english"></a>
## English

A web application built with Streamlit to inspect, format, and compare JSONs with AI capabilities.

### Features

- 🎨 **JSON Formatting**: Format and validate JSON structures
- 🤖 **AI Analysis**: Ask questions about JSON structure and content using Groq AI
- 🔍 **Comparison**: Compare two JSONs and show their differences
- 🌐 **Internationalization**: Supports English and Spanish
- 📝 **History**: Keeps track of formatted JSONs

### Requirements

- Python 3.8+
- Streamlit
- Requests
- DeepDiff
- python-dotenv

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/json-ai-inspector.git
cd json-ai-inspector
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) To use AI features, configure your Groq API key:
```bash
echo "GROQ_API_KEY=your-api-key" > .env
```

4. Run the application:
```bash
streamlit run app.py
```

<a name="español"></a>
## Español

Una aplicación web construida con Streamlit para inspeccionar, formatear y comparar JSONs con capacidades de IA.

### Características

- 🎨 **Formateo de JSON**: Formatea y valida estructuras JSON
- 🤖 **Análisis con IA**: Hace preguntas sobre la estructura y contenido del JSON usando Groq AI
- 🔍 **Comparación**: Compara dos JSONs y muestra sus diferencias
- 🌐 **Internacionalización**: Soporta Español e Inglés
- 📝 **Historial**: Mantiene un historial de los JSONs formateados

### Requisitos

- Python 3.8+
- Streamlit
- Requests
- DeepDiff
- python-dotenv

### Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/your-username/json-ai-inspector.git
cd json-ai-inspector
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. (Opcional) Para usar las funciones de IA, configura tu API key de Groq:
```bash
echo "GROQ_API_KEY=tu-api-key" > .env
```

4. Ejecuta la aplicación:
```bash
streamlit run app.py
```
