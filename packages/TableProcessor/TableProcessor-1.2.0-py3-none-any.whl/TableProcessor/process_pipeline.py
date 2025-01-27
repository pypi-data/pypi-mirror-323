import os
import time
from .utils import load_data, convertir_valor, segundos_a_segundos_minutos_y_horas
from .blank import editar_vacios
from .processing import process_data


def process_pipeline(input_path, output_xlsx_path, config):
    """
    Ejecuta el flujo de procesamiento.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"El archivo de entrada no existe: {input_path}")

    # Asegurarte de que el directorio de salida exista
    os.makedirs(os.path.dirname(output_xlsx_path), exist_ok=True)

    start_time = time.time()

    # 1) Definimos la ruta del CSV intermedio sustituyendo {-SB} por -SB
    #    y cambiando la extensión a .csv
    intermediate_csv_path = (
        output_xlsx_path
        .replace("{-SB}", "-SB")
        .replace(".xlsx", ".csv")
    )

    # 2) Definimos la ruta del XLSX final eliminando por completo {-SB}
    final_output_xlsx_path = (
        output_xlsx_path
        .replace("{-SB}", "")
    )

    # Cargar y procesar los datos
    lines = load_data(input_path)
    df = process_data(lines)

    # Transformar la columna "Periodo" si existe
    if "Periodo" in df.columns:
        df["Periodo"] = df["Periodo"].apply(convertir_valor)

    # Guardar el DataFrame como un archivo CSV intermedio
    print("Guardando csv intermedio...")
    df.to_csv(intermediate_csv_path, index=False, encoding="ISO-8859-1")

    # Blanquear/editar vacíos y guardar el XLSX con el nombre final
    editar_vacios(config, df, final_output_xlsx_path)

    elapsed_time = time.time() - start_time
    formatted_time = segundos_a_segundos_minutos_y_horas(elapsed_time)
    print(f"Proceso completado en {formatted_time}.")
