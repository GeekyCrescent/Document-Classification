import os
import json
import multiprocessing
from transformers import LayoutLMv3Processor
from PIL import Image
from tqdm import tqdm  # ✅ Barra de progreso

# ✅ Cargar el procesador LayoutLMv3
processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")

# ✅ Definir el mapeo de etiquetas solo para "CUENTA" y "CURP"
label_mapping = {
    "CV": 12
}

def procesar_archivo(args):
    """Función para procesar un archivo de texto e imagen."""
    txt_path, img_path, label_id, original_txt_path, original_img_path = args

    if not os.path.exists(img_path):
        print(f"⚠️ Imagen no encontrada: {img_path}, omitiendo...")
        return None

    try:
        # Leer el texto
        with open(txt_path, "r", encoding="utf-8") as f:
            texto = f.read()

        # Cargar imagen
        img = Image.open(img_path)

        # Procesar datos con LayoutLMv3Processor
        encoding = processor(images=img, text=texto, return_tensors="pt", truncation=True, max_length=512)

        # Validar que todos los campos están presentes
        if all(key in encoding for key in ["input_ids", "bbox", "pixel_values", "attention_mask"]):
            return {
                "input_ids": encoding["input_ids"].squeeze().tolist(),
                "bbox": encoding["bbox"].squeeze().tolist(),
                "pixel_values": encoding["pixel_values"].squeeze().tolist(),
                "attention_mask": encoding["attention_mask"].squeeze().tolist(),
                "label": label_id,
                "imagen": original_img_path,  # ✅ Guardamos la ruta original de Google Drive
                "texto": texto
            }
    except Exception as e:
        print(f"❌ Error procesando {txt_path}: {e}")

    return None

def cargar_datos(carpeta_principal, categorias):
    """Carga los datos de las categorías especificadas en paralelo usando multiprocessing con barra de progreso."""
    datos = []
    tareas = []

    for categoria in categorias:
        categoria_path = os.path.join(carpeta_principal, categoria)

        if not os.path.isdir(categoria_path):
            print(f"⚠️ Carpeta no encontrada: {categoria_path}, omitiendo...")
            continue

        label_id = label_mapping.get(categoria, -1)
        if label_id == -1:
            print(f"⚠️ Categoría desconocida: {categoria}, omitiendo...")
            continue

        for subcarpeta in os.listdir(categoria_path):
            subcarpeta_path = os.path.join(categoria_path, subcarpeta)

            if not os.path.isdir(subcarpeta_path):
                continue

            for archivo in os.listdir(subcarpeta_path):
                if archivo.endswith(".txt"):
                    txt_path = os.path.join(subcarpeta_path, archivo)
                    img_path = txt_path.replace(".txt", ".jpg")

                    original_txt_path = txt_path.replace("/content/", "/content/drive/MyDrive/")
                    original_img_path = img_path.replace("/content/", "/content/drive/MyDrive/")

                    tareas.append((txt_path, img_path, label_id, original_txt_path, original_img_path))

    # ✅ Procesar archivos en paralelo con barra de progreso
    resultados = []
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        for resultado in tqdm(pool.imap(procesar_archivo, tareas), total=len(tareas), desc="Procesando archivos"):
            if resultado is not None:
                resultados.append(resultado)

    return resultados

# ✅ Ruta en Google Drive donde están los datos procesados
base_path = "/content/drive/MyDrive/ModeloGrande/TextoImagenes"
categorias_a_procesar = ["CV"]

# ✅ Cargar los datos correctamente con barra de progreso
datos_entrenamiento = cargar_datos(base_path, categorias_a_procesar)

print(f"📂 Datos procesados: {len(datos_entrenamiento)} elementos.")

# ✅ Guardar el JSON en Google Drive
json_output_path = "/content/drive/MyDrive/ModeloGrande/JSON/datos_CV.json"

if datos_entrenamiento:
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(datos_entrenamiento, f, ensure_ascii=False, indent=4)
    print(f"✅ JSON creado y guardado en Google Drive: {json_output_path}")
else:
    print("⚠️ No se encontraron datos para guardar.")
