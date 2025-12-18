import calendar
import cdsapi
import sys
# --- Paràmetres ---
if len(sys.argv) < 2:
    print("❌ Error: No has passat cap any.")
    print("Ús: python el_teu_script.py <ANY>")
    sys.exit()  # Això tanca el programa immediatament

# 2. Capturem el paràmetre
parametre = sys.argv[1]
ANY = int(parametre)
AREA_VALENCIA = [39.6, -0.5, 39.3, -0.2] # [N, W, S, E]
DATASET = "reanalysis-era5-single-levels"

# *** DIVIDIM LES VARIABLES ***
VARIABLES_INST = [
    '10m_u_component_of_wind',   # Component U del vent (per a 'u10')
    '10m_v_component_of_wind',   # Component V del vent (per a 'v10')
    '2m_dewpoint_temperature',   # Temp. de rosada (per a 'd2m', calcular HR)
    '2m_temperature',            # Temperatura (per a 't2m')
]

VARIABLES_ACCUM = [
    'surface_net_solar_radiation', # Radiació solar neta (per a 'ssr')
    'surface_net_thermal_radiation', # Radiació tèrmica neta (per a 'str')
]

# Plantilla de la petició
request_template = {
    'product_type': 'reanalysis',
    'format': 'grib',
    'area': AREA_VALENCIA,
    'time': [ # Les 24 hores del dia
        "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"
    ],
}

# --- Execució ---
# ... (codi del client cdsapi) ...
client = cdsapi.Client()
# Bucle per a descarregar els 12 mesos
for mes_num in range(1, 13):
#for mes_num in range (1,2):

    
    mes_str = f"{mes_num:02d}" # Formata el mes com "01", "02", etc.
    num_dies = calendar.monthrange(int(ANY), mes_num)[1]
    llista_dies = [f"{dia:02d}" for dia in range(1, num_dies + 1)]

    print(f"--- Processant Mes: {mes_str} ---")

    # --- PETICIÓ 1: Dades Instantànies ---
    nom_arxiu_inst = f"DataSets{ANY}/{ANY}{mes_str}_era5_instantani.grib"
    request_inst = request_template.copy()
    request_inst['variable'] = VARIABLES_INST
    request_inst['year'] = ANY
    request_inst['month'] = mes_str
    request_inst['day'] = llista_dies
    
    print(f"Demanant dades INSTANTÀNIES a l'API... (es guardarà com a '{nom_arxiu_inst}')")
    try:
        client.retrieve(DATASET, request_inst, nom_arxiu_inst)
        print(f"Arxiu '{nom_arxiu_inst}' descarregat amb èxit.")
    except Exception as e:
        print(f"ERROR en descarregar dades instantànies: {e}")

    # --- PETICIÓ 2: Dades Acumulades ---
    nom_arxiu_accum = f"DataSets{ANY}/{ANY}{mes_str}_era5_acumulat.grib"
    request_accum = request_template.copy()
    request_accum['variable'] = VARIABLES_ACCUM
    request_accum['year'] = ANY
    request_accum['month'] = mes_str
    request_accum['day'] = llista_dies
    
    print(f"Demanant dades ACUMULADES a l'API... (es guardarà com a '{nom_arxiu_accum}')")
    try:
        client.retrieve(DATASET, request_accum, nom_arxiu_accum)
        print(f"Arxiu '{nom_arxiu_accum}' descarregat amb èxit.")
    except Exception as e:
        print(f"ERROR en descarregar dades acumulades: {e}")

print(f"\nDescàrrega per a l'any {ANY} completada.")
