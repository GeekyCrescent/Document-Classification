import json
import os

def json_to_jsonl(input_file, output_file=None):
    """
    Convierte un archivo JSON que contiene un array de objetos a formato JSONL.

    Args:
        input_file (str): Ruta al archivo JSON de entrada
        output_file (str, opcional): Ruta al archivo JSONL de salida.
            Si no se proporciona, usará el nombre del archivo de entrada con extensión .jsonl

    Returns:
        str: Ruta al archivo JSONL creado
    """
    # Determinar nombre del archivo de salida si no se proporciona
    if output_file is None:
        if input_file.endswith('.json'):
            output_file = input_file[:-5] + '.jsonl'
        else:
            output_file = input_file + '.jsonl'

    try:
        # Leer los datos JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Asegurar que los datos son una lista/array
        if not isinstance(data, list):
            raise ValueError("El JSON de entrada debe contener un array/lista de objetos")

        # Escribir cada objeto como una línea en el archivo de salida
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')

        print(f"Conversión exitosa: {input_file} a {output_file}")
        print(f"Se convirtieron {len(data)} objetos JSON a formato JSONL")
        return output_file

    except json.JSONDecodeError:
        print(f"Error: {input_file} contiene JSON inválido")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Ejemplo de uso:
# Cambia estas rutas según tus necesidades
input_file = "/content/drive/MyDrive/ModeloGrande/JSONL/datos_SEGVIDA.json"  # Ruta a tu archivo JSON
output_file = "/content/drive/MyDrive/ModeloGrande/JSONL/datos_SEGVIDA.jsonl"  # Opcional, ruta para el archivo JSONL

# Para ejecutar la conversión, descomenta la siguiente línea:
resultado = json_to_jsonl(input_file, output_file)
