import pandas as pd
import numpy as np
import math
import sys

# --- Constants Físiques ---
ALTITUD_VALENCIA = 11.0  # Metres sobre el nivell del mar
LAMBDA = 2.45  # Calor latent de vaporització (MJ/kg)
CP = 1.013e-3  # Calor específica de l'aire (MJ/kg°C)
EPSILON = 0.622 # Relació de pesos moleculars vapor/aire

def calcular_fao56(row):
    """
    Implementació de l'equació FAO-56 Penman-Monteith
    """
    # 1. Variables d'entrada des del CSV
    T_mean = row['T_media_C_AEMET']  # Fem servir AEMET per a temp (més real)
    RH_mean = row['HR_media_ERA5']   # ERA5 per a humitat
    u2 = row['Vent_2m_ms_ERA5']      # ERA5 per a vent
    Rn = row['Rn_MJ_dia']            # ERA5 per a radiació
    
    # Si falta alguna dada, no podem calcular
    if pd.isna([T_mean, RH_mean, u2, Rn]).any():
        return np.nan

    # 2. Càlculs intermedis
    
    # Pressió atmosfèrica (P) en kPa (depén de l'altitud)
    P = 101.3 * ((293 - 0.0065 * ALTITUD_VALENCIA) / 293) ** 5.26
    
    # Constant psicromètrica (gamma)
    gamma = (CP * P) / (EPSILON * LAMBDA)
    
    # Pendent de la corba de pressió de vapor (delta)
    delta = (4098 * (0.6108 * np.exp((17.27 * T_mean) / (T_mean + 237.3)))) / ((T_mean + 237.3) ** 2)
    
    # Pressió de vapor de saturació (es)
    es = 0.6108 * np.exp((17.27 * T_mean) / (T_mean + 237.3))
    
    # Pressió de vapor actual (ea)
    ea = es * (RH_mean / 100.0)
    
    # Dèficit de pressió de vapor (es - ea)
    vpd = es - ea
    
    # Flux de calor del sòl (G). Per a càlculs diaris, sovint s'assumeix G ≈ 0
    G = 0 
    
    # 3. L'Equació Final Penman-Monteith
    numerador = (0.408 * delta * (Rn - G)) + (gamma * (900 / (T_mean + 273)) * u2 * vpd)
    denominador = delta + (gamma * (1 + 0.34 * u2))
    
    et0 = numerador / denominador
    
    # Evitem valors negatius (físicament impossibles, però poden passar per errors de dades)
    return max(0, et0)


  # PAS DE SEGURETAT: Netejar índexs corruptes
if len(sys.argv) < 2:
    print("❌ Error: No has passat cap any.")
    print("Ús: python el_teu_script.py <ANY>")
    sys.exit()  # Això tanca el programa immediatament

        # 2. Capturem el paràmetre
any_a_processar = sys.argv[1]
    # CANVIA AÇÒ SI ESTÀS FENT EL 2025
carpetaDatasets = "DataSets"+any_a_processar+"/"  # O "DataSets/" per a l'any
# --- Execució ---

print("Llegint dades unificades...")
df = pd.read_csv(f'{carpetaDatasets}dades_unificades_{any_a_processar}.csv', index_col=0, parse_dates=True)

print("Calculant ET0 diària segons mètode FAO-56...")
df['ET0_Calculada'] = df.apply(calcular_fao56, axis=1)

# Guardem el resultat
output_file = f'{carpetaDatasets}dades_amb_ET0_{any_a_processar}.csv'
df.to_csv(output_file)

print(f"\nCàlcul completat.")
print(f"Arxiu guardat: {output_file}")
print("\nExemple de les dades calculades:")
print(df[['T_media_C_AEMET', 'Rn_MJ_dia', 'ET0_Calculada']].head())
print(f"\nMitjana de ET0 en {any_a_processar}: {df['ET0_Calculada'].mean():.2f} mm/dia")
