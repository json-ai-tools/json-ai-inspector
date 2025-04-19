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
import re
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional, Union, Tuple
import pandas as pd
from io import StringIO


def infer_type(value: Any) -> str:
    """Inferir el tipo de un valor JSON.

    Args:
        value: Valor a analizar

    Returns:
        str: Nombre del tipo inferido
    """
    if isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, str):
        # Detectar patrones comunes
        if re.match(r'^\d{4}-\d{2}-\d{2}', value):  # Fecha
            return "date"
        elif re.match(r'^[a-fA-F0-9]{24}$', value):  # ObjectId
            return "objectId"
        elif re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', value):  # UUID
            return "uuid"
        elif '@' in value:  # Email
            return "email"
        elif re.match(r'^\+?\d{1,4}[-.\s]?\(?\d{1,}\)?[-.\s]?\d{1,}[-.\s]?\d{1,}$', value):  # Teléfono
            return "phone"
        elif re.match(r'^https?://', value):  # URL
            return "url"
        else:
            return "string"
    elif isinstance(value, list):
        if not value:
            return "array"
        # Inferir tipo del primer elemento no nulo
        for item in value:
            if item is not None:
                return f"array<{infer_type(item)}>"
        return "array"
    elif isinstance(value, dict):
        return "object"
    elif value is None:
        return "null"
    else:
        return "any"


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
        json_str: String JSON a formatear

    Returns:
        Tuple[bool, str, Optional[Dict[str, Any]]]: (éxito, resultado, datos)
    """
    try:
        # Validar y formatear JSON
        data = json.loads(json_str)
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        return True, formatted, data
    except json.JSONDecodeError as e:
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


def generate_python_type(name: str, properties: Dict[str, Any], level: int = 0) -> str:
    """Genera una clase Python a partir de un objeto JSON.

    Args:
        name: Nombre de la clase
        properties: Propiedades y sus tipos
        level: Nivel de indentación

    Returns:
        str: Código Python con la definición de la clase
    """
    indent = "    " * level
    type_mappings = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "null": "None",
        "date": "datetime",
        "objectId": "str",
        "uuid": "str",
        "email": "str",
        "phone": "str",
        "url": "str",
        "any": "Any"
    }

    class_def = [f"{indent}@dataclass"]
    class_def.append(f"{indent}class {name}:")
    
    # Agregar docstring
    class_def.append(f"{indent}    \"\"\"{name} model.\"\"\"")
    
    # Agregar imports necesarios
    imports = set(["from dataclasses import dataclass"])
    if "Any" in str(properties):
        imports.add("from typing import Any")
    if "List" in str(properties) or "array" in str(properties):
        imports.add("from typing import List")
    if "datetime" in str(properties):
        imports.add("from datetime import datetime")

    # Procesar propiedades
    for prop_name, prop_type in properties.items():
        if isinstance(prop_type, dict):
            # Generar clase anidada
            nested_name = prop_name.title()
            nested_class = generate_python_type(nested_name, prop_type, level + 1)
            class_def.insert(-1, "\n" + nested_class)
            class_def.append(f"{indent}    {prop_name}: {nested_name}")
        elif prop_type.startswith("array"):
            # Manejar arrays
            item_type = prop_type[6:-1]  # Extraer tipo dentro de array<...>
            if item_type == "object":
                nested_name = f"{prop_name.title()}Item"
                class_def.append(f"{indent}    {prop_name}: List[{nested_name}]")
            else:
                mapped_type = type_mappings.get(item_type, item_type)
                class_def.append(f"{indent}    {prop_name}: List[{mapped_type}]")
        else:
            # Tipos básicos
            mapped_type = type_mappings.get(prop_type, prop_type)
            class_def.append(f"{indent}    {prop_name}: {mapped_type}")

    return "\n".join(class_def)


def generate_typescript_type(name: str, properties: Dict[str, Any], level: int = 0) -> str:
    """Genera una interfaz TypeScript a partir de un objeto JSON.

    Args:
        name: Nombre de la interfaz
        properties: Propiedades y sus tipos
        level: Nivel de indentación

    Returns:
        str: Código TypeScript con la definición de la interfaz
    """
    indent = "  " * level
    type_mappings = {
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "null": "null",
        "date": "Date",
        "objectId": "string",
        "uuid": "string",
        "email": "string",
        "phone": "string",
        "url": "string",
        "any": "any"
    }

    interface_def = [f"{indent}export interface {name} {{"]

    # Procesar propiedades
    for prop_name, prop_type in properties.items():
        if isinstance(prop_type, dict):
            # Generar interfaz anidada
            nested_name = f"{name}{prop_name.title()}"
            nested_interface = generate_typescript_type(nested_name, prop_type, level + 1)
            interface_def.insert(-1, nested_interface + "\n")
            interface_def.append(f"{indent}  {prop_name}: {nested_name};")
        elif prop_type.startswith("array"):
            # Manejar arrays
            item_type = prop_type[6:-1]  # Extraer tipo dentro de array<...>
            if item_type == "object":
                nested_name = f"{name}{prop_name.title()}Item"
                interface_def.append(f"{indent}  {prop_name}: {nested_name}[];")
            else:
                mapped_type = type_mappings.get(item_type, item_type)
                interface_def.append(f"{indent}  {prop_name}: {mapped_type}[];")
        else:
            # Tipos básicos
            mapped_type = type_mappings.get(prop_type, prop_type)
            interface_def.append(f"{indent}  {prop_name}: {mapped_type};")

    interface_def.append(indent + "}")
    return "\n".join(interface_def)


def generate_golang_type(name: str, properties: Dict[str, Any], level: int = 0) -> str:
    """Genera una estructura Go a partir de un objeto JSON.

    Args:
        name: Nombre de la estructura
        properties: Propiedades y sus tipos
        level: Nivel de indentación

    Returns:
        str: Código Go con la definición de la estructura
    """
    indent = "\t" * level
    type_mappings = {
        "string": "string",
        "integer": "int64",
        "number": "float64",
        "boolean": "bool",
        "null": "interface{}",
        "date": "time.Time",
        "objectId": "string",
        "uuid": "string",
        "email": "string",
        "phone": "string",
        "url": "string",
        "any": "interface{}"
    }

    struct_def = ["// Package models contiene las estructuras de datos\npackage models\n"] if level == 0 else []
    struct_def.append(f"{indent}// {name} representa {name.lower()}")
    struct_def.append(f"{indent}type {name} struct {{")

    # Procesar propiedades
    for prop_name, prop_type in properties.items():
        json_tag = f'`json:"{prop_name}"`'
        if isinstance(prop_type, dict):
            # Generar estructura anidada
            nested_name = f"{name}{prop_name.title()}"
            nested_struct = generate_golang_type(nested_name, prop_type, level + 1)
            struct_def.insert(-1, nested_struct + "\n")
            struct_def.append(f"{indent}\t{prop_name.title()} {nested_name} {json_tag}")
        elif prop_type.startswith("array"):
            # Manejar arrays
            item_type = prop_type[6:-1]  # Extraer tipo dentro de array<...>
            if item_type == "object":
                nested_name = f"{name}{prop_name.title()}Item"
                struct_def.append(f"{indent}\t{prop_name.title()} []{nested_name} {json_tag}")
            else:
                mapped_type = type_mappings.get(item_type, item_type)
                struct_def.append(f"{indent}\t{prop_name.title()} []{mapped_type} {json_tag}")
        else:
            # Tipos básicos
            mapped_type = type_mappings.get(prop_type, prop_type)
            struct_def.append(f"{indent}\t{prop_name.title()} {mapped_type} {json_tag}")

    struct_def.append(indent + "}")
    return "\n".join(struct_def)


def analyze_json_structure(json_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Analiza la estructura de un JSON y devuelve un diccionario con los tipos inferidos.

    Args:
        json_data: JSON string o diccionario a analizar

    Returns:
        Dict[str, Any]: Diccionario con los tipos inferidos
    """
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    def infer_field_type(field_name: str, values: List[Any]) -> str:
        """Infiere el tipo de un campo basado en su nombre y valores de ejemplo."""
        # Normalizar el nombre del campo
        field_name = field_name.lower()

        # Tipos basados en el nombre del campo
        if any(x in field_name for x in ['id', 'uuid', 'guid']):
            return "objectId"
        elif any(x in field_name for x in ['email', 'mail']):
            return "email"
        elif any(x in field_name for x in ['phone', 'tel', 'mobile', 'cellular']):
            return "phone"
        elif any(x in field_name for x in ['url', 'website', 'web', 'link']):
            return "url"
        elif any(x in field_name for x in ['date', 'time', 'created', 'updated', 'timestamp']):
            return "date"
        elif any(x in field_name for x in ['age', 'count', 'number', 'qty', 'quantity', 'index']):
            return "integer"
        elif any(x in field_name for x in ['price', 'amount', 'score', 'rating', 'percentage']):
            return "number"
        elif any(x in field_name for x in ['is_', 'has_', 'active', 'enabled', 'status', 'bool']):
            return "boolean"
        elif any(x in field_name for x in ['tags', 'categories', 'items', 'list']):
            return "array<string>"

        # Si no se puede inferir por nombre, intentar inferir por los valores de ejemplo
        for value in values:
            if isinstance(value, bool):
                return "boolean"
            elif isinstance(value, int):
                return "integer"
            elif isinstance(value, float):
                return "number"
            elif isinstance(value, str):
                # Intentar inferir el tipo basado en el formato del string
                if re.match(r'^[0-9a-fA-F]{24}$', value):
                    return "objectId"
                elif re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', value):
                    return "uuid"
                elif re.match(r'^[\w\.-]+@[\w\.-]+\.[\w]{2,}$', value):
                    return "email"
                elif re.match(r'^\+?[1-9][0-9]{7,14}$', value):
                    return "phone"
                elif re.match(r'^https?://[\w\.-]+\.[\w]{2,}[\w\.-/_]*$', value):
                    return "url"
                elif re.match(r'^\d{4}-\d{2}-\d{2}', value):
                    return "date"

        # Por defecto, retornar string
        return "string"

    def analyze_value(value: Any) -> Union[str, Dict[str, Any]]:
        if isinstance(value, dict):
            # Recolectar todos los valores de ejemplo para cada campo
            field_values = {}
            if isinstance(json_data, list):
                for item in json_data:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            if k not in field_values:
                                field_values[k] = []
                            field_values[k].append(v)
            else:
                for k, v in value.items():
                    field_values[k] = [v]

            # Inferir tipos para cada campo
            return {k: analyze_value(v) if isinstance(v, dict) else 
                      infer_field_type(k, field_values.get(k, [])) 
                   for k, v in value.items()}
        elif isinstance(value, list):
            if not value:
                return "array<string>"
            # Analizar el primer elemento no nulo
            for item in value:
                if item is not None:
                    if isinstance(item, dict):
                        return f"array<object>"
                    return f"array<{infer_type(item)}>"
            return "array<string>"
        else:
            return infer_type(value)

    # Si es una lista, analizar la estructura del primer objeto
    if isinstance(json_data, list) and json_data:
        first_item = next((item for item in json_data if isinstance(item, dict)), None)
        if first_item:
            return analyze_value(first_item)

    return analyze_value(json_data)


def generate_dummy_data(value_type: str) -> Any:
    """Genera un valor dummy basado en el tipo.

    Args:
        value_type: Tipo de valor a generar

    Returns:
        Any: Valor generado
    """
    if value_type.startswith("array<"):
        inner_type = value_type[6:-1]  # Extraer el tipo dentro del array<tipo>
        num_items = random.randint(1, 5)
        return [generate_dummy_data(inner_type) for _ in range(num_items)]
    elif value_type == "string":
        words = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit"]
        return " ".join(random.choices(words, k=random.randint(1, 4)))
    elif value_type == "integer":
        return random.randint(-1000, 1000)
    elif value_type == "number":
        return round(random.uniform(-1000, 1000), 2)
    elif value_type == "boolean":
        return random.choice([True, False])
    elif value_type == "date":
        days = random.randint(-1000, 1000)
        return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    elif value_type == "objectId":
        return ''.join(random.choices(string.hexdigits.lower(), k=24))
    elif value_type == "uuid":
        return str(uuid.uuid4())
    elif value_type == "email":
        domains = ["example.com", "test.com", "dummy.org", "sample.net"]
        username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
        return f"{username}@{random.choice(domains)}"
    elif value_type == "phone":
        return f"+{random.randint(1, 99)}{random.randint(100000000, 999999999)}"
    elif value_type == "url":
        domains = ["example.com", "test.com", "dummy.org", "sample.net"]
        paths = ["api", "docs", "blog", "users", "products"]
        return f"https://{random.choice(domains)}/{random.choice(paths)}"
    elif value_type == "null":
        return None
    else:
        return "dummy_value"


def generate_dummy_object(structure: Dict[str, Any]) -> Dict[str, Any]:
    """Genera un objeto dummy basado en la estructura.

    Args:
        structure: Estructura del objeto

    Returns:
        Dict[str, Any]: Objeto dummy generado
    """
    result = {}
    for key, value_type in structure.items():
        if isinstance(value_type, dict):
            result[key] = generate_dummy_object(value_type)
        elif isinstance(value_type, str) and value_type.startswith("array"):
            # Generar array con 1-5 elementos
            item_type = value_type[6:-1]  # Extraer tipo dentro de array<...>
            if item_type == "object":
                result[key] = [generate_dummy_object({"item": "string"})["item"] for _ in range(random.randint(1, 5))]
            else:
                result[key] = [generate_dummy_data(item_type) for _ in range(random.randint(1, 5))]
        else:
            result[key] = generate_dummy_data(value_type)
    return result


def generate_mock_data(json_data: Union[str, Dict[str, Any]], num_records: int = 10) -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
    """Genera datos dummy basados en la estructura del JSON.

    Args:
        json_data: JSON string o diccionario a analizar
        num_records: Número de registros a generar (máx. 1000)

    Returns:
        Tuple[bool, str, Optional[List[Dict[str, Any]]]]: (éxito, mensaje de error, datos generados)
    """
    if num_records > 1000:
        return False, "El número de registros no puede ser mayor al máximo permitido (1000)", None

    try:
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
    except json.JSONDecodeError:
        return False, "JSON inválido", None

    try:
        # Analizar estructura
        structure = analyze_json_structure(json_data)

        # Generar registros
        records = [generate_dummy_object(structure) for _ in range(num_records)]

        return True, "", records
    except Exception as e:
        return False, f"Error al generar datos dummy: {str(e)}", None


def generate_types(json_data: Union[str, Dict[str, Any]], base_name: str = "Root") -> Tuple[bool, str, Dict[str, str]]:
    """Genera tipos para diferentes lenguajes a partir de un JSON.

    Args:
        json_data: JSON string o diccionario a analizar
        base_name: Nombre base para las clases/interfaces/estructuras

    Returns:
        Tuple containing:
        - bool: True si la generación fue exitosa
        - str: Mensaje de error si falla
        - Dict[str, str]: Diccionario con el código generado para cada lenguaje
    """
    try:
        # Analizar estructura
        structure = analyze_json_structure(json_data)

        # Generar tipos para cada lenguaje
        python_code = generate_python_type(base_name, structure)
        typescript_code = generate_typescript_type(base_name, structure)
        golang_code = generate_golang_type(base_name, structure)

        return True, "", {
            "python": python_code,
            "typescript": typescript_code,
            "golang": golang_code
        }
    except Exception as e:
        return False, f"Error al generar tipos: {str(e)}", {}


def json_to_csv(json_data: Union[str, Dict[str, Any]]) -> Tuple[bool, str, Optional[str]]:
    """Convert JSON to CSV format with intelligent column ordering and formatting.

    Args:
        json_data: JSON string or dictionary to convert

    Returns:
        Tuple containing:
        - bool: True if conversion was successful
        - str: Error message if failed, empty string if successful
        - Optional[str]: CSV string if successful, None if failed
    """
    try:
        # Si es string, convertir a diccionario
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        # Si tenemos un objeto 'result' que contiene un array, usar el contenido del array
        if isinstance(json_data, dict) and 'result' in json_data and isinstance(json_data['result'], list):
            # Ignorar el primer elemento si es una directiva 'repeat'
            content = json_data['result'][1] if len(json_data['result']) > 1 else json_data['result'][0]
            json_data = [content] if isinstance(content, dict) else content
        # Si es un diccionario simple, convertirlo a lista
        elif isinstance(json_data, dict):
            json_data = [json_data]

        # Convertir a DataFrame con manejo especial de datos anidados
        df = pd.json_normalize(
            json_data,
            sep='.',  # Usar punto como separador para niveles anidados
            max_level=None  # No limitar la profundidad de anidamiento
        )

        # Ordenar columnas de manera inteligente por grupos
        columns = list(df.columns)
        ordered_columns = []

        # 1. IDs y campos de identificación
        id_fields = ['id', 'uuid', 'objectId', 'username', 'email']
        id_columns = [col for col in columns if any(id_field in col.lower() for id_field in id_fields)]
        ordered_columns.extend(sorted(id_columns))

        # 2. Información personal básica
        personal_fields = ['name', 'first', 'last', 'middle', 'phone', 'password', 'status', 'message']
        personal_columns = [col for col in columns 
                          if any(field in col.lower() for field in personal_fields)
                          and col not in ordered_columns]
        ordered_columns.extend(sorted(personal_columns))

        # 3. Información de localización
        location_fields = ['location', 'address', 'street', 'city', 'state', 'country', 'zip', 'coordinates']
        location_columns = [col for col in columns 
                          if any(field in col.lower() for field in location_fields)
                          and col not in ordered_columns]
        ordered_columns.extend(sorted(location_columns))

        # 4. Información profesional
        job_fields = ['job', 'company', 'website', 'domain']
        job_columns = [col for col in columns 
                      if any(field in col.lower() for field in job_fields)
                      and col not in ordered_columns]
        ordered_columns.extend(sorted(job_columns))

        # 5. Información financiera
        financial_fields = ['creditCard', 'payment', 'bank']
        financial_columns = [col for col in columns 
                           if any(field in col.lower() for field in financial_fields)
                           and col not in ordered_columns]
        ordered_columns.extend(sorted(financial_columns))

        # 6. Arrays y campos restantes
        remaining_columns = [col for col in columns if col not in ordered_columns]
        ordered_columns.extend(sorted(remaining_columns))

        # Reordenar el DataFrame
        df = df[ordered_columns]

        # Limpiar nombres de columnas para mejor legibilidad
        clean_columns = []
        for col in df.columns:
            # Mantener la notación de array con []  
            if '[' in col:
                base_name = col.split('[')[0]
                array_index = col[col.find('['):]
                clean_name = base_name.replace('.', ' ').title() + array_index
            else:
                clean_name = col.replace('.', ' ').title()
            clean_columns.append(clean_name)
        
        df.columns = clean_columns

        # Convertir a CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_string = csv_buffer.getvalue()

        return True, "", csv_string
    except Exception as e:
        return False, f"Error al convertir a CSV: {str(e)}", None
