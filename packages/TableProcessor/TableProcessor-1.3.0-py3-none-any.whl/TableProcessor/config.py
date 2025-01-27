CONFIG = {
    "input_path": "./files/Tabs-DB-Vinson.CSV",
    "output_path": "./output/Vinson-24 Q4-Datos_Dashboard{-SB}-R5.xlsx"
}

REL_BASES_TABLA = {
    1: "Total",
    2: "Frecuencia",
    3: "Conoce-Intención",
    4: "Conoce-Consideración",
    5: "Conoce-Imagen"
}

BLANQUEAR_CONFIG = {
    "blanquear": [
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q4 18",
            "demo": "Marca",
            "valores": ["Epura", "Ciel", "Bonafont", "Santa Maria", "Pureza Vital"],
            "base_var": None,
            "lista_vars": "BPS Y COMPONENTES"
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 19",
            "periodo_fin": "Q3 19",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": ["Es la que me da más valor por mi dinero"]
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q2 20",
            "demo": "Marca",
            "valores": ["Skarch"],
            "base_var": None,
            "lista_vars": "BPS Y COMPONENTES"
        },

        # SEGMENTOS BRS
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q3 18",
            "demo": "Marca",
            "valores": "__All__",
            "base_var": None,
            "lista_vars": "SEGMENTOS-BRS"
        },
        {
            "mantener": False,
            "periodo_ini": "Q2 20",
            "periodo_fin": "Q2 20",
            "demo": "Marca",
            "valores": [
                "Skarch",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": "SEGMENTOS-BRS"
        },

        # FRECUENCIA
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q4 14",
            "demo": "Marca",
            "valores": "__All__",
            "base_var": None,
            "lista_vars": "FRECUENCIA"
        },

        # INTENCIÓN DE COMPRA
        {
            "mantener": True,
            "periodo_ini": "Q4 18",
            "periodo_fin": "Actual",
            "demo": "Marca",
            "valores": "__All__",
            "base_var": None,
            "lista_vars": "INTENCION DE COMPRA"
        },
        {
            "mantener": False,
            "periodo_ini": "Q2 20",
            "periodo_fin": None,
            "demo": "Marca",
            "valores": [
                "Skarch",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": "INTENCION DE COMPRA"
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q1 17",
            "demo": "Marca",
            "valores": ["Skarch"],
            "base_var": None,
            "lista_vars": "CONSIDERACION"
        },

        # Imagen
        {
            "mantener": False,
            "periodo_ini": "Q2 18",
            "periodo_fin": "Actual",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "01 Da confianza",
                "02 Es de la que todos hablan",
                "03 Vale lo que cuesta",
                "06 Es tu marca favorita",
                "07 No tiene sodio",
                "09 Quita la sed",
                "10 Tiene empaque atractivo",
                "12 Es experta en agua embotellada natural",
                "14 Ayuda a que mi cuerpo funcione",
                "15 Ayuda a cuidar tu peso",
                "17 Ayuda a recuperarte después del ejercicio",
                "20 Es una marca que me hace sentir vivo y activo",
                "21 Ayuda a mantener tu cuerpo en armonía y balance"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q1 13",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": ["22 Me ayuda a experimentar un bienestar profundo"]
        },
        {
            "mantener": False,
            "periodo_ini": "Q2 18",
            "periodo_fin": "Actual",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": ["22 Me ayuda a experimentar un bienestar profundo"]
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q1 15",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "27 Te ayuda a amar tu cuerpo",
                "29 Te ayuda a sentirte bien contigo mismo(a)"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Q2 18",
            "periodo_fin": "Actual",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "27 Te ayuda a amar tu cuerpo",
                "29 Te ayuda a sentirte bien contigo mismo(a)"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Q3 15",
            "periodo_fin": "Actual",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "16 Permite llevar una vida más sana",
                "18 Te hace sentir bien por dentro",
                "19 Te reanima / reactiva"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q1 15",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "26 Me mantiene bien hidratado",
                "28 Me hace consciente de lo maravilloso que es mi cuerpo"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q1 18",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "41 Ofrece productos diferentes al agua natural"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Q3 19",
            "periodo_fin": "Actual",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "41 Ofrece productos diferentes al agua natural"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q1 18",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "30 Siempre tiene comerciales",
                "31 Tiene la mejor publicidad",
                "32 Tiene la botella más atractiva",
                "33 Da la seguridad de que está 100% purificada",
                "34 Está más a la vista cuando la voy a comprar",
                "35 Me ayuda a tomar más agua",
                "36 Me ayuda a mejorar mi salud",
                "37 Tiene un empaque práctico",
                "38 Tiene todo lo que debe de tener el agua",
                "39 Me ayuda a que todo mi cuerpo se active",
                "40 Me ayuda a eliminar todo lo malo",
                "42 Me ayuda a que todo mi cuerpo funcione correctamente",
                "43 Es para cualquier actividad",
                "44 Está presente en eventos atractivos para mi",
                "45 Tiene promociones atractivas"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q2 19",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "46 Me ayuda a cuidar mi cuerpo",
                "47 Me ayuda a estar en armonía"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q3 19",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "48 Es la que me da más valor por mi dinero"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Q1 13",
            "periodo_fin": "Q2 23",
            "demo": "Marca",
            "valores": [
                "Epura",
                "Ciel",
                "Bonafont",
                "Santa Maria",
                "Pureza Vital"
            ],
            "base_var": None,
            "lista_vars": [
                "49 Se comporta responsablemente con el medio ambiente"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Inicio",
            "periodo_fin": "Actual",
            "demo": "Marca",
            "valores": ["Skarch"],
            "base_var": None,
            "lista_vars": [
                "01 Da confianza",
                "02 Es de la que todos hablan",
                "03 Vale lo que cuesta",
                "06 Es tu marca favorita",
                "07 No tiene sodio",
                "09 Quita la sed",
                "10 Tiene empaque atractivo",
                "12 Es experta en agua embotellada natural",
                "14 Ayuda a que mi cuerpo funcione",
                "15 Ayuda a cuidar tu peso",
                "16 Permite llevar una vida más sana",
                "17 Ayuda a recuperarte después del ejercicio",
                "18 Te hace sentir bien por dentro",
                "19 Te reanima / reactiva",
                "20 Es una marca que me hace sentir vivo y activo",
                "21 Ayuda a mantener tu cuerpo en armonía y balance",
                "22 Me ayuda a experimentar un bienestar profundo",
                "27 Te ayuda a amar tu cuerpo",
                "29 Te ayuda a sentirte bien contigo mismo(a)",
                "41 Ofrece productos diferentes al agua natural"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Inicio",
            "periodo_fin": "Q2 20",
            "demo": "Marca",
            "valores": ["Skarch"],
            "base_var": None,
            "lista_vars": [
                "04 Es para todos los días",
                "05 Es una marca que amo",
                "08 Es ligera",
                "11 Tiene buen sabor",
                "13 Es amigable con el medio ambiente",
                "23 Es innovadora",
                "24 Ofrece algo diferente a las otras marcas",
                "25 Es refrescante",
                "26 Me mantiene bien hidratado",
                "28 Me hace consciente de lo maravilloso que es mi cuerpo",
                "30 Siempre tiene comerciales",
                "31 Tiene la mejor publicidad",
                "32 Tiene la botella más atractiva",
                "33 Da la seguridad de que está 100% purificada",
                "34 Está más a la vista cuando la voy a comprar",
                "35 Me ayuda a tomar más agua",
                "36 Me ayuda a mejorar mi salud",
                "37 Tiene un empaque práctico",
                "38 Tiene todo lo que debe de tener el agua",
                "39 Me ayuda a que todo mi cuerpo se active",
                "40 Me ayuda a eliminar todo lo malo",
                "42 Me ayuda a que todo mi cuerpo funcione correctamente",
                "43 Es para cualquier actividad",
                "44 Está presente en eventos atractivos para mi",
                "45 Tiene promociones atractivas",
                "46 Me ayuda a cuidar mi cuerpo",
                "47 Me ayuda a estar en armonía",
                "48 Es la que me da más valor por mi dinero"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Inicio",
            "periodo_fin": "Q2 23",
            "demo": "Marca",
            "valores": ["Skarch"],
            "base_var": None,
            "lista_vars": [
                "49 Se comporta responsablemente con el medio ambiente"
            ]
        },

        # Cambio en 2024-Q4 (atributos de imagen que quitaron)
        {
            "mantener": False,
            "periodo_ini": "Q4 24",
            "periodo_fin": "Actual",
            "demo": "Marca",
            "valores": "__All__",
            "base_var": None,
            "lista_vars": [
                "36 Me ayuda a mejorar mi salud",
                "40 Me ayuda a eliminar todo lo malo",
                "42 Me ayuda a que todo mi cuerpo funcione correctamente",
                "47 Me ayuda a estar en armonía",
                "49 Se comporta responsablemente con el medio ambiente"
            ]
        },

        # No Conocedor
        {
            "mantener": False,
            "periodo_ini": "Inicio",
            "periodo_fin": "Actual",
            "demo": "Demografico",
            "valores": ["No Conocedor"],
            "base_var": None,
            "lista_vars": "KPIS DE CONOCIMIENTO Y CONSUMO"
        },
        {
            "mantener": False,
            "periodo_ini": "Inicio",
            "periodo_fin": "Actual",
            "demo": "Demografico",
            "valores": ["No Conocedor"],
            "base_var": None,
            "lista_vars": "FRECUENCIA"
        },
        {
            "mantener": False,
            "periodo_ini": "Inicio",
            "periodo_fin": "Actual",
            "demo": "Demografico",
            "valores": ["No Conocedor"],
            "base_var": None,
            "lista_vars": "INTENCION DE COMPRA"
        },
        {
            "mantener": False,
            "periodo_ini": "Inicio",
            "periodo_fin": "Actual",
            "demo": "Demografico",
            "valores": ["No Conocedor"],
            "base_var": None,
            "lista_vars": "CONSIDERACION"
        },
        {
            "mantener": False,
            "periodo_ini": "Inicio",
            "periodo_fin": "Actual",
            "demo": "Demografico",
            "valores": ["No Conocedor"],
            "base_var": None,
            "lista_vars": "BPS Y COMPONENTES"
        },
        {
            "mantener": False,
            "periodo_ini": "Inicio",
            "periodo_fin": "Actual",
            "demo": "Demografico",
            "valores": ["No Conocedor"],
            "base_var": None,
            "lista_vars": [
                "Leales",
                "Switchers",
                "Potenciales",
                "Esporádicos",
                "No interesados",
                "Abandonador"
            ]
        },
        {
            "mantener": False,
            "periodo_ini": "Inicio",
            "periodo_fin": "Actual",
            "demo": "Demografico",
            "valores": ["No Conocedor"],
            "base_var": None,
            "lista_vars": "BATERIA DE IMAGEN"
        }
    ],

    # ####### Listas
    "listas": {
        "KPIS DE CONOCIMIENTO Y CONSUMO": [
            "TOM",
            "C. Espotáneo",
            "C.Total",
            "Trial",
            "P4W",
            "P7D"
        ],
        "FRECUENCIA": [
            "Todos los días / Diario",
            "4 - 6 veces a la semana",
            "2 - 3 veces a la semana",
            "Una vez por semana",
            "Una vez cada 2 semanas",
            "Una vez al mes",
            "Menos de una vez al mes",
            "Solo consumió una vez",
            "MEAN"
        ],
        "INTENCION DE COMPRA": [
            "Definitivamente SI lo compraría",
            "Probablemente SI lo compraría",
            "Tal vez SI tal vez NO lo compraría",
            "Probablemente NO lo compraría",
            "Definitivamente NO lo compraría"
        ],
        "CONSIDERACION": [
            "Es la ÚNICA marca que consideraría",
            "Es una de 2 ó 3 marcas que consideraría",
            "Es una de muchas marcas que consideraría",
            "Es una marca que quizá NO consideraría",
            "Es una marca que NUNCA consideraría"
        ],
        "BPS Y COMPONENTES": [
            "Brand Power Score",
            "Salience",
            "Preference",
            "Relevance",
            "Distinction",
            "Salience TOM",
            "Salience C. Espotáneo",
            "Top Box (Es la unica marca que consideraría)",
            "Second Box (Es una de 2-3 marcas que consideraria)",
            "Es una marca que amo",
            "Tiene Buen sabor",
            "Es la que me da más valor por mi dinero",
            "Me ayuda a tomar más agua",
            "Es para todos los días",
            "Tiene la mejor publicidad",
            "Ofrece algo diferente a las otras marcas",
            "Es innovadora"
        ],
        "SEGMENTOS-BRS": [
            "Leales",
            "Switchers",
            "Potenciales",
            "Esporádicos",
            "No interesados",
            "Abandonador",
            "No Conocedor"
        ],
        "BATERIA DE IMAGEN": [
            "01 Da confianza",
            "02 Es de la que todos hablan",
            "03 Vale lo que cuesta",
            "04 Es para todos los días",
            "05 Es una marca que amo",
            "06 Es tu marca favorita",
            "07 No tiene sodio",
            "08 Es ligera",
            "09 Quita la sed",
            "10 Tiene empaque atractivo",
            "11 Tiene buen sabor",
            "12 Es experta en agua embotellada natural",
            "13 Es amigable con el medio ambiente",
            "14 Ayuda a que mi cuerpo funcione",
            "15 Ayuda a cuidar tu peso",
            "16 Permite llevar una vida más sana",
            "17 Ayuda a recuperarte después del ejercicio",
            "18 Te hace sentir bien por dentro",
            "19 Te reanima / reactiva",
            "20 Es una marca que me hace sentir vivo y activo",
            "21 Ayuda a mantener tu cuerpo en armonía y balance",
            "22 Me ayuda a experimentar un bienestar profundo",
            "23 Es innovadora",
            "24 Ofrece algo diferente a las otras marcas",
            "25 Es refrescante",
            "26 Me mantiene bien hidratado",
            "27 Te ayuda a amar tu cuerpo",
            "28 Me hace consciente de lo maravilloso que es mi cuerpo",
            "29 Te ayuda a sentirte bien contigo mismo(a)",
            "30 Siempre tiene comerciales",
            "31 Tiene la mejor publicidad",
            "32 Tiene la botella más atractiva",
            "33 Da la seguridad de que está 100% purificada",
            "34 Está más a la vista cuando la voy a comprar",
            "35 Me ayuda a tomar más agua",
            "36 Me ayuda a mejorar mi salud",
            "37 Tiene un empaque práctico",
            "38 Tiene todo lo que debe de tener el agua",
            "39 Me ayuda a que todo mi cuerpo se active",
            "40 Me ayuda a eliminar todo lo malo",
            "41 Ofrece productos diferentes al agua natural",
            "42 Me ayuda a que todo mi cuerpo funcione correctamente",
            "43 Es para cualquier actividad",
            "44 Está presente en eventos atractivos para mi",
            "45 Tiene promociones atractivas",
            "46 Me ayuda a cuidar mi cuerpo",
            "47 Me ayuda a estar en armonía",
            "48 Es la que me da más valor por mi dinero",
            "49 Se comporta responsablemente con el medio ambiente"
        ]
    }
}

import process_pipeline


# Función principal
def main():
    try:
        process_pipeline.process_pipeline(CONFIG['input_path'], CONFIG['output_path'], CONFIG)
    except Exception as e:
        print(f"Error: {e}")


# Ejecución del script
if __name__ == "__main__":
    main()
