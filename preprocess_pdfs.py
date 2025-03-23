import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import multiprocessing
from tqdm import tqdm

def extraer_datos(pdf_path, output_folder):
    """Extrae texto, convierte a imagen y guarda texto en archivo .txt por página (máx. 5 páginas)."""
    doc = fitz.open(pdf_path)
    datos = []

    # Obtener nombre base del PDF (sin extensión)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Convertir solo las primeras 5 páginas a imágenes
    images = convert_from_path(pdf_path, first_page=1, last_page=5)

    for i, image in enumerate(images):
        page_num = i + 1  # Numeración de páginas comienza en 1
        
        # Generar nombres de archivos evitando repeticiones
        img_filename = f"{pdf_name}_pagina_{page_num}.jpg"
        txt_filename = f"{pdf_name}_pagina_{page_num}.txt"

        img_path = os.path.join(output_folder, img_filename)
        txt_path = os.path.join(output_folder, txt_filename)

        # Guardar la imagen
        image.save(img_path, "JPEG")

        # Extraer texto con OCR
        texto = pytesseract.image_to_string(image, lang="spa")

        # Guardar el texto extraído en un archivo .txt
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(texto)

        datos.append({"texto": texto, "imagen": img_path, "txt": txt_path})

    return datos

def procesar_pdf(pdf_path_output):
    pdf_path, output_folder = pdf_path_output
    try:
        return extraer_datos(pdf_path, output_folder)
    except Exception as e:
        print(f"❌ Error procesando {os.path.basename(pdf_path)}: {e}")
        return []

def procesar_carpeta(carpeta, output_base):
    """Procesa todos los PDFs dentro de una carpeta en paralelo con barra de progreso."""
    os.makedirs(output_base, exist_ok=True)
    pdf_paths = []
    
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".pdf"):
            pdf_path = os.path.join(carpeta, archivo)
            pdf_output_folder = os.path.join(output_base, os.path.splitext(archivo)[0])
            os.makedirs(pdf_output_folder, exist_ok=True)
            pdf_paths.append((pdf_path, pdf_output_folder))
    
    datos_entrenamiento = []
    with multiprocessing.Pool() as pool:
        for resultado in tqdm(pool.imap(procesar_pdf, pdf_paths), total=len(pdf_paths), desc="Procesando PDFs"):
            datos_entrenamiento.extend(resultado)
    
    return datos_entrenamiento

if __name__ == "__main__":
    base_path = r"CarpetasPorDocumento"
    output_base = r"DatosProcesados"
    categorias = ["CONPROB"]
    datos_finales = {}

    for categoria in categorias:
        input_folder = os.path.join(base_path, categoria)
        output_folder = os.path.join(output_base, categoria)
        datos_finales[categoria] = procesar_carpeta(input_folder, output_folder)

    print("✅ Datos procesados y guardados correctamente.")
