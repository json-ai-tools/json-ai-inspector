# 🧠 JSON AI Inspector

[English](#english) | [Español](#español)

<a name="english"></a>
## English

A Streamlit application for JSON analysis, comparison, and data generation using AI.

## Features

### 1. JSON Formatting
- Pretty print JSON with syntax highlighting
- Export to CSV for Excel compatibility
- Generate type definitions for Python, Go, and TypeScript

### 2. AI Analysis
- Ask questions about your JSON in natural language
- Get intelligent responses powered by Groq AI
- Contextual understanding of JSON structure

### 3. JSON Comparison
- Compare two JSON structures side by side
- Highlight differences and changes
- Detailed comparison report

### 4. Mock Data Generation
- Generate sample data based on JSON structure
- Support for common data types:
  - Basic types: string, integer, number, boolean
  - Date and time formats
  - Special types: email, phone, url, objectId
  - Arrays with type inference
- History of generated datasets
- Export generated data

### Additional Features
- Internationalization (Spanish/English)
- Session state management
- History tracking
- Dark/Light mode support
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
- 📊 **Exportación CSV**: Convierte JSON a CSV para compatibilidad con Excel
- 🎲 **Generación de Datos de Prueba**: Genera datos de ejemplo y definiciones de tipos para:
  - Python
  - Golang
  - TypeScript

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
