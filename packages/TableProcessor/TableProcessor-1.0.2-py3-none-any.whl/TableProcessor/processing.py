import pandas as pd
import numpy as np
from tqdm import tqdm

# Importa el mapeo de nombres de tabla directamente desde tu config.py
from files.config import REL_BASES_TABLA

# Importa las funciones desde utils.py
from utils import is_numeric, extract_column_data


def process_data(lines):
    """
    Procesa las tablas (Tabla 1, Tabla 2, ...) generando un DataFrame donde cada
    combinación (Marca, Ciudad, Corte, Demografico, Periodo, Quiebre) quede en
    una sola fila. En este ajuste, SOLO queremos los porcentajes.

    - Si la variable viene en 2 líneas (la segunda empieza con ""), ignoramos la
      primera (valores absolutos) y usamos la segunda como porcentajes.
    - Si la variable solo tiene 1 línea (ej. "Prac-Mean"), esa línea misma se
      asume que trae porcentajes.

    Nota: Ahora ya no recibimos ni usamos un archivo YAML. El mapeo de tablas
    se hace con el diccionario REL_BASES_TABLA importado desde config.py.
    """

    # -------------------------------------------------------------------------
    # 1) Cargar el mapeo de nombres de tabla desde config.py
    # -------------------------------------------------------------------------
    rel_bases = REL_BASES_TABLA

    # -------------------------------------------------------------------------
    # 2) Diccionario principal, para no duplicar filas.
    #    Clave = (Marca, Ciudad, Corte, Demografico, Periodo, Quiebre)
    #    Valor = dict con el resto de columnas, p.ej. "Trial", "Abandonador", etc.
    # -------------------------------------------------------------------------
    records_dict = {}

    # -------------------------------------------------------------------------
    # 3) Variables auxiliares para el bucle
    # -------------------------------------------------------------------------
    current_page = 0
    table_start = -1

    # -------------------------------------------------------------------------
    # 4) Recorrer fila a fila
    # -------------------------------------------------------------------------
    for i, row in enumerate(tqdm(lines, desc="Procesando Tablas", colour="red")):
        if not row:  # Fila vacía
            continue

        # 4.1) Detectar cambio de página (#page)
        if row[0].strip().startswith("#page"):
            current_page += 1
            table_start = i
            continue

        # 4.2) Detectar "Tabla X"
        if row[0].lower().startswith("tabla") and table_start != -1:
            table_str = row[0].strip()
            parts = table_str.split()
            table_number = None
            if len(parts) > 1 and parts[0].lower() == "tabla":
                try:
                    table_number = int(parts[1])
                except ValueError:
                    table_number = None

            if not table_number:
                continue  # No se parseó

            # -----------------------------------------------------------------
            # 5) Extraer datos fijos (Marca, Ciudad, Corte, Demográfico)
            # -----------------------------------------------------------------
            try:
                marca, ciudad, corte, demografico = "", "", "", ""

                # Nombre de la tabla (offset +6) — si lo necesitas
                if len(lines) > table_start + 6 and len(lines[table_start + 6]) > 0:
                    _ = lines[table_start + 6][0].strip().strip('"')

                # Marca (offset +7)
                if len(lines) > table_start + 7 and len(lines[table_start + 7]) > 0:
                    marca = lines[table_start + 7][0].strip().strip('"')

                # Ciudad (offset +8)
                if len(lines) > table_start + 8 and len(lines[table_start + 8]) > 0:
                    ciudad = lines[table_start + 8][0].strip().strip('"')

                # Corte/Demográfico (offset +9)
                if len(lines) > table_start + 9 and len(lines[table_start + 9]) > 0:
                    corte_demografico_line = lines[table_start + 9][0]
                    if ":" in corte_demografico_line:
                        parts_corte = corte_demografico_line.split(":")
                        corte = parts_corte[0].strip().strip('"')
                        demografico = parts_corte[1].strip().strip('"')
                    else:
                        corte = corte_demografico_line.strip().strip('"')
                        demografico = corte

                # ----------------------------------------------------------------
                # 6) Buscar "Base Ponderada"
                # ----------------------------------------------------------------
                bp_index = None
                for j in range(table_start, len(lines)):
                    if len(lines[j]) > 0:
                        first_cell = lines[j][0].strip().strip('"').lower()
                        if first_cell.startswith("base ponderada"):
                            bp_index = j
                            break

                if bp_index is not None:
                    # Periodos están 2 filas antes
                    if bp_index - 2 >= 0 and len(lines[bp_index - 2]) > 1:
                        periodos_line = lines[bp_index - 2][1:]
                    else:
                        periodos_line = []

                    # Extraer la Base Ponderada
                    base_ponderada_extracted = extract_column_data(lines, bp_index, 1)
                    base_tabla_name = rel_bases.get(table_number, f"SinNombre_{table_number}")
                    base_column_name = f"Base {base_tabla_name}"

                    # Guardar la base
                    for idx, periodo in enumerate(periodos_line):
                        periodo_clean = periodo.strip().replace('"', "")
                        quiebre = "Año" if is_numeric(periodo_clean) else "Trimestre"
                        key = (marca, ciudad, corte, demografico, periodo_clean, quiebre)
                        if key not in records_dict:
                            records_dict[key] = {
                                "Marca": marca,
                                "Ciudad": ciudad,
                                "Corte": corte,
                                "Demografico": demografico,
                                "Periodo": periodo_clean,
                                "Quiebre": quiebre,
                            }
                        if idx < len(base_ponderada_extracted):
                            records_dict[key][base_column_name] = base_ponderada_extracted[idx]
                        else:
                            records_dict[key][base_column_name] = np.nan

                    # -----------------------------------------------------------------
                    # 6.5) Extraer SOLO porcentajes (una o dos líneas)
                    # -----------------------------------------------------------------
                    index = bp_index + 1
                    while index < len(lines):
                        row_current = lines[index]
                        if not row_current:
                            index += 1
                            continue

                        first_cell_clean = row_current[0].strip().lower()

                        # Fin de sección si llegamos a una nueva "tabla" o "#page"
                        if first_cell_clean.startswith("#page") or first_cell_clean.startswith("tabla"):
                            break

                        # Nombre de la variable
                        column_name = row_current[0].strip().strip('"')
                        if not column_name:
                            # Sin nombre => no procesamos
                            index += 1
                            continue

                        # Mirar si la siguiente línea (index+1) es la subfila de porcentajes
                        # (primer elemento vacío)
                        next_line_is_subfila = False
                        if (index + 1) < len(lines):
                            row_next = lines[index + 1]
                            if row_next and len(row_next) > 0 and not row_next[0].strip():
                                next_line_is_subfila = True

                        if next_line_is_subfila:
                            # CASO: 2 líneas => la primera son absolutos, la segunda = porcentajes
                            # 1) ignoramos la primera (absolutos)
                            _ = extract_column_data(lines, index, 1)

                            # 2) extraemos la segunda (porcentajes)
                            second_line_values = extract_column_data(lines, index + 1, 1)

                            # Asignamos second_line_values al records_dict
                            for idx2, val in enumerate(second_line_values):
                                if idx2 < len(periodos_line):
                                    periodo_clean = periodos_line[idx2].strip().replace('"', "")
                                    quiebre = "Año" if is_numeric(periodo_clean) else "Trimestre"
                                    key = (marca, ciudad, corte, demografico, periodo_clean, quiebre)

                                    if key not in records_dict:
                                        records_dict[key] = {
                                            "Marca": marca,
                                            "Ciudad": ciudad,
                                            "Corte": corte,
                                            "Demografico": demografico,
                                            "Periodo": periodo_clean,
                                            "Quiebre": quiebre,
                                        }
                                    records_dict[key][column_name] = val

                            # saltamos 2 filas
                            index += 2
                        else:
                            # CASO: 1 sola línea => esta misma línea tiene los porcentajes
                            single_line_values = extract_column_data(lines, index, 1)

                            # Asignamos single_line_values
                            for idx2, val in enumerate(single_line_values):
                                if idx2 < len(periodos_line):
                                    periodo_clean = periodos_line[idx2].strip().replace('"', "")
                                    quiebre = "Año" if is_numeric(periodo_clean) else "Trimestre"
                                    key = (marca, ciudad, corte, demografico, periodo_clean, quiebre)

                                    if key not in records_dict:
                                        records_dict[key] = {
                                            "Marca": marca,
                                            "Ciudad": ciudad,
                                            "Corte": corte,
                                            "Demografico": demografico,
                                            "Periodo": periodo_clean,
                                            "Quiebre": quiebre,
                                        }
                                    records_dict[key][column_name] = val

                            # saltamos 1 fila
                            index += 1
                else:
                    print(f"No se encontró 'Base Ponderada' para la tabla en la página {current_page}.")

            except Exception as e:
                print(f"Error procesando la tabla en línea {i}: {e}")

    # -------------------------------------------------------------------------
    # 7) Construir el DataFrame final
    # -------------------------------------------------------------------------
    df = pd.DataFrame(records_dict.values())

    return df
