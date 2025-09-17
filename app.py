import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

# ------------------------
# CONFIGURACIÓN
# ------------------------
EXCEL_PATH = "chotico.xlsx"
PLANTILLA_PATH = "fernandez.png"
OUTPUT_DIR = "boletas_generadas"

# Crear carpeta de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Leer Excel
df = pd.read_excel(EXCEL_PATH, dtype=str)

# Plantilla
plantilla = Image.open(PLANTILLA_PATH).convert("RGB")

# Fuentes
try:
    font_encabezado = ImageFont.truetype("Arial.ttf", 50)  # Encabezado
    font_casillas = ImageFont.truetype("arial.ttf", 40)    # Números
except:
    font_encabezado = ImageFont.load_default()
    font_casillas = ImageFont.load_default()

# Coordenadas
casilla_width = 104
casilla_height = 40
start_x, start_y = 500, 885
coords_casillas = [
    (start_x + i * (casilla_width + 30), start_y,
     start_x + (i+1) * casilla_width, start_y + casilla_height)
    for i in range(4)
]

coord_nombre = (200, 70)
coord_direccion = (200, 160)
coord_celular = (200, 240)

# ------------------------
# FUNCIÓN PARA GENERAR BOLETA
# ------------------------
def generar_boleta(numero, nombre, direccion, celular):
    # Normalizar número a 3 dígitos
    numero = str(numero).zfill(3)

    # Buscar en Excel
    fila = df[(df["N1"].astype(str).str.zfill(3) == numero) |
              (df["N2"].astype(str).str.zfill(3) == numero) |
              (df["N3"].astype(str).str.zfill(3) == numero) |
              (df["N4"].astype(str).str.zfill(3) == numero)]

    if fila.empty:
        return None, f"⚠ El número {numero} no existe en el Excel."

    fila = fila.iloc[0]

    # Copiar plantilla
    img = plantilla.copy()
    draw = ImageDraw.Draw(img)

    # Encabezado
    draw.text(coord_nombre, f"{nombre}", fill="black", font=font_encabezado)
    draw.text(coord_direccion, f"{direccion}", fill="black", font=font_encabezado)
    draw.text(coord_celular, f"{celular}", fill="black", font=font_encabezado)

    # Casillas con números
    for i, col in enumerate(["N1", "N2", "N3", "N4"]):
        x0, y0, x1, y1 = coords_casillas[i]
        num = str(fila[col]).zfill(3)
        bbox = draw.textbbox((0, 0), num, font=font_casillas)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        text_x = x0 + (casilla_width - w) / 2
        text_y = y0 + (casilla_height - h) / 2
        draw.text((text_x, text_y), num, fill="red", font=font_casillas)

    # Guardar boleta
    file_name = f"boleta_{numero}.png"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    img.save(file_path)

    return file_path, f"✅ Boleta generada: {file_path}"

# ------------------------
# INTERFAZ STREAMLIT
# ------------------------
st.title("🎟 Generador de Boletas")

numero = st.text_input("Número de boleta (N):")
nombre = st.text_input("Nombre del cliente:")
direccion = st.text_input("Dirección:")
celular = st.text_input("Celular:")

if st.button("Generar Boleta"):
    # Limpiar entradas
    numero_val = numero.strip()
    nombre_val = nombre.strip()
    direccion_val = direccion.strip()
    celular_val = celular.strip()

    if numero_val and nombre_val and direccion_val and celular_val:
        file_path, msg = generar_boleta(numero_val, nombre_val, direccion_val, celular_val)
        if file_path:
            st.success(msg)
            st.image(file_path, caption="Boleta generada", use_container_width=True)
            with open(file_path, "rb") as f:
                st.download_button("⬇ Descargar boleta", f, file_name=os.path.basename(file_path))
        else:
            st.error(msg)
    else:
        st.error("⚠ Por favor complete todos los campos (no pueden estar vacíos).")