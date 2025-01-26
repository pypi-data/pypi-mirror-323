# blank.py

import numpy as np
from main import BLANQUEAR_CONFIG

def guardar_excel(df, nom_arch):
    print(f'Guardando dashboard [{nom_arch}] en excel...')
    df.to_excel(nom_arch, merge_cells=False)
    print('Guardado.')


def guardar_csv(df, nom_arch):
    print(f'Guardando dashboard [{nom_arch}] en csv...')
    df.to_csv(nom_arch, encoding='ISO-8859-1')
    print('Guardado.')


def calcular_inicio_y_actual(df):
    l_anios = df.loc[df.Quiebre == 'Año', 'Periodo'].unique()
    anio_act = max(l_anios)
    anio_ini = min(l_anios)

    l_trimestres = df.loc[df.Quiebre == 'Trimestre', 'Periodo'].unique()
    anio_act_trim = max([int(an[-2:]) for an in l_trimestres])  # + 2000
    trim_act = None
    trim_ini = None

    # Importante: Se asume que ninguna medición es anterior al año 2000
    for q in range(1, 5):
        # Va de Q1 a Q4
        if trim_ini is None and f'Q{q} {anio_ini - 2000}' in l_trimestres:
            trim_ini = f'Q{q} {anio_ini - 2000}'
        # Va de Q4 a Q1
        if trim_act is None and f'Q{5 - q} {anio_act_trim}' in l_trimestres:
            trim_act = f'Q{5 - q} {anio_act_trim}'

    return anio_act, anio_ini, trim_act, trim_ini


def editar_vacios(yml, df_ent, n_sal):
    print('Leyendo archivo para blanquear')
    print('Blanqueando')
    listas = BLANQUEAR_CONFIG['listas']
    l_blanquear = BLANQUEAR_CONFIG['blanquear']

    anio_actual, anio_principio, trimestre_actual, trimestre_principio = calcular_inicio_y_actual(df_ent)

    for blanquear in l_blanquear:
        # Se obtiene la lista de variables a blanquear
        l_vars = blanquear['lista_vars']
        if isinstance(l_vars, str):
            l_vars = listas[l_vars]

        # Se agrega a la lista la variable de la base si se blanquea
        var_base = blanquear['base_var']
        if var_base is not None:
            l_vars = [var_base] + l_vars

        # Se obtienen los años y trimestres que se blanquean
        periodo_inicio = blanquear['periodo_ini']
        mantener = blanquear['mantener']
        if periodo_inicio == 'Inicio':
            periodo_inicio = trimestre_principio
            anio_inicio = anio_principio
        else:
            anio_inicio = int(periodo_inicio[-2:]) if 'Q1' in periodo_inicio or mantener else int(
                periodo_inicio[-2:]) + 1
            anio_inicio += 2000

        l_trims = {periodo_inicio}
        l_ans = []
        periodo_fin = blanquear['periodo_fin']
        if periodo_fin is not None:
            if periodo_fin == 'Actual':
                periodo_fin = trimestre_actual
                anio_fin = anio_actual
            else:
                anio_fin = int(periodo_fin[-2:]) if 'Q4' in periodo_fin or mantener else int(periodo_fin[-2:]) - 1
                anio_fin += 2000

            # Importante: Se asume que el formato de los trimestres en las tablas es: "Q\d \d\d"
            q_ini, a_ini = int(periodo_inicio[1:2]), int(periodo_inicio[-2:])
            q_fin, a_fin = int(periodo_fin[1:2]), int(periodo_fin[-2:])

            if a_ini != a_fin:
                # Se agregan los Q del primer año
                for q_tmp in range(q_ini + 1, 5):
                    l_trims.add(f'Q{q_tmp} {a_ini}')
                # Se agregan los Q de los años de en medio si los hay
                if a_ini + 1 <= a_fin - 1:
                    for a_tmp in range(a_ini + 1, a_fin):
                        for q_tmp in range(1, 5):
                            l_trims.add(f'Q{q_tmp} {a_tmp}')
                # Se agregan los Q del último año
                for q_tmp in range(1, q_fin + 1):
                    l_trims.add(f'Q{q_tmp} {a_fin}')
            else:
                for q_tmp in range(q_ini, q_fin + 1):
                    l_trims.add(f'Q{q_tmp} {a_fin}')

            # Se agregan los años que se blanquean si los hay
            if anio_inicio <= anio_fin:
                l_ans.extend([a for a in range(anio_inicio, anio_fin + 1)])

        l_periodos_blanquear = list(l_trims) + l_ans
        assert l_periodos_blanquear, f'No hay periodos con el rango seleccionado:\n\tIni: {blanquear["periodo_ini"]}\n\tFin: {blanquear["periodo_fin"]}'

        # Se ajusta la lista de acuerdo a la acción
        if mantener:
            # l_periodos_blanquear.extend([min(l_ans) - 1, max(l_ans) + 1])
            l_periodos_blanquear = [per for per in df_ent.loc[df_ent.Quiebre == 'Trimestre', 'Periodo'].unique() if
                                    per not in l_periodos_blanquear]

        vals_blanc_mask = df_ent.Periodo.isin(l_periodos_blanquear)
        if blanquear['valores'] != '__All__':
            vals_blanc_mask = vals_blanc_mask & df_ent.loc[:, blanquear['demo']].isin(blanquear['valores'])
        df_ent.loc[vals_blanc_mask, l_vars] = np.nan

    df_ent.set_index(['Marca', 'Ciudad', 'Corte', 'Demografico', 'Periodo', 'Quiebre'], inplace=True)

    guardar_excel(df_ent, n_sal)
    guardar_csv(df_ent, n_sal.replace('.xlsx', '.csv'))



