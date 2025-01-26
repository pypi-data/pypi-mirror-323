import csv
import numpy as np
import pandas as pd
import yaml


def is_numeric(s):
    """Verifica si una cadena es numérica o es un guion '-'."""
    if s == "-" or s is None or s.strip() == "":
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def convert_to_numeric(value):
    """
    Convierte una cadena a un número, reemplaza '-' o vacío por 0.
    """
    if value is None:
        return 0
    if isinstance(value, str):
        value = value.strip()
        if value == "-" or value == "":
            return 0
    return float(value)



def safe_convert(value):
    """Convierte valores en números de forma segura, manejando None y vacíos."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return np.nan
    return convert_to_numeric(value)


def load_data(input_path):
    """
    Carga los datos desde un archivo CSV y devuelve una lista de listas,
    donde cada sub-lista corresponde a una fila ya dividida por comas,
    respetando el contenido entre comillas.
    """
    with open(input_path, "r", encoding="ISO-8859-1") as file:
        reader = csv.reader(file, quotechar='"', delimiter=",")
        return [row for row in reader]


def extract_column_data(lines, start_index, length):
    """
    Extrae y convierte datos de columnas desde una o varias filas específicas.
    lines: lista de listas (cada sub-lista es una fila).
    start_index: índice de la fila donde comenzar a extraer.
    length: cuántas filas leer desde 'start_index'.

    Retorna una lista con los valores (después de safe_convert).
    """
    values = []
    for row in lines[start_index: start_index + length]:
        # row[1:] => columnas desde la 2da en adelante
        for value in row[1:]:
            values.append(safe_convert(value))
    return values

def convertir_valor(valor):
    """
    Convierte un número almacenado como texto en un valor numérico.
    Si no es un número, lo deja como está.
    """
    try:
        return int(valor)  # Mantener como int si es un número
    except ValueError:
        return valor  # Mantener como str si no es convertible

def save_with_xlsxwriter(df, output_xlsx_path):
    """
    Guarda un DataFrame a un archivo .xlsx rápidamente usando xlsxwriter.
    """
    print(f"Exportando a excel {output_xlsx_path}...")
    with pd.ExcelWriter(output_xlsx_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet 1')
    print(f"Guardado completado en {output_xlsx_path}.")



def segundos_a_segundos_minutos_y_horas(segundos):
    horas = int(segundos / 3600)
    segundos -= horas * 3600
    minutos = int(segundos / 60)
    segundos -= minutos * 60
    return f"{horas:02d}:{minutos:02d}:{int(segundos):02d}"

