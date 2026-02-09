import pdfplumber
import re
import os
from fpdf import FPDF

# 1. Configuración de rutas
FOLDER_IN = "entradas/"
FOLDER_OUT = "salidas/"

def extraer_datos(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto = pdf.pages[0].extract_text()
    
    # Extracción con expresiones regulares (basado en tu documento)
    datos = {
        "id": re.search(r"ID del Paciente: ([\d-]+)", texto).group(1),
        "nombre": re.search(r"Nombre: (\w+)", texto).group(1) + " " + re.search(r"Apellido: ([\w\s]+)", texto).group(1),
        "fecha": re.search(r"Fecha de Prueba: ([\d-]+)", texto).group(1),
        "feno50": re.search(r"Valor de FeN050: (\d+)", texto).group(1),
        "cano": re.search(r"CaNO#:\s?([\d,.]+)", texto).group(1) if "CaNO#" in texto else "N/A"
    }
    return datos

def generar_pdf(datos, nombre_salida):
    pdf = FPDF()
    pdf.add_page()
    
    # Estética Profesional
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "INFORME DE FUNCIÓN PULMONAR (FeNO)", ln=True, align="C")
    pdf.ln(10)
    
    # Cuadro de paciente
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, f" Paciente: {datos['nombre']} | ID: {datos['id']}", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f" Fecha de estudio: {datos['fecha']}", ln=True)
    pdf.ln(5)
    
    # Resultado Destacado
    val = int(datos['feno50'])
    color = (200, 0, 0) if val > 50 else (0, 150, 0) # Rojo si es alto, verde si es bajo
    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Resultado Principal:", ln=True)
    pdf.set_text_color(*color)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 15, f"FeNO 50: {val} ppb", ln=True, align="C")
    
    # Interpretación
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "I", 10)
    interp = "Nivel bajo: Inflamación eosinofílica poco probable." if val < 25 else "Nivel alto: Sugiere inflamación eosinofílica activa."
    pdf.multi_cell(0, 10, f"Interpretación Clínica: {interp}", align="C")
    
    pdf.output(os.path.join(FOLDER_OUT, nombre_salida))

# Procesar todos los archivos en la carpeta entradas
if __name__ == "__main__":
    for archivo in os.listdir(FOLDER_IN):
        if archivo.endswith(".pdf"):
            print(f"Procesando {archivo}...")
            data = extraer_datos(os.path.join(FOLDER_IN, archivo))
            generar_pdf(data, f"Informe_{data['id']}.pdf")
