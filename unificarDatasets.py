#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per a unificar les dades d'AEMET (JSON) i ERA5 (GRIB).
VERSIÓ ROBUSTA: Ordenació per coordenades internes.
"""

import pandas as pd
import xarray as xr
import glob
import json
import numpy as np
import sys
import os

  # PAS DE SEGURETAT: Netejar índexs corruptes
if len(sys.argv) < 2:
    print("❌ Error: No has passat cap any.")
    print("Ús: python el_teu_script.py <ANY>")
    sys.exit()  # Això tanca el programa immediatament

        # 2. Capturem el paràmetre
any_a_processar = sys.argv[1]
    # CANVIA AÇÒ SI ESTÀS FENT EL 2025
carpetaDatasets = "DataSets"+any_a_processar+"/"  # O "DataSets/" per al 2024
def carregar_dades_aemet():
    print("--- 1. Processant Dades AEMET (JSON) ---")
    arxius_json = glob.glob(os.path.join(carpetaDatasets, '*Aemet*.json'))
    
    if not arxius_json:
        print(f"ERROR: No s'han trobat arxius '*Aemet*.json' a: {carpetaDatasets}")
        return None

    totes_dades_aemet = []
    for arxiu in arxius_json:
        try:
            with open(arxiu, 'r', encoding='utf-8') as f:
                dades = json.load(f)
                if isinstance(dades, list):
                    totes_dades_aemet.extend(dades)
        except Exception as e:
            print(f"Error llegint '{arxiu}': {e}")

    if not totes_dades_aemet:
        print("ERROR: No hi ha dades AEMET vàlides.")
        return None

    df_aemet = pd.DataFrame(totes_dades_aemet)

    # Neteja
    if 'fecha' in df_aemet.columns:
        df_aemet['fecha'] = pd.to_datetime(df_aemet['fecha'])
        df_aemet = df_aemet.set_index('fecha')
    
    cols_numeriques = ['tmed', 'tmax', 'tmin', 'prec', 'sol']
    for col in cols_numeriques:
        if col in df_aemet.columns:
            if col == 'prec': df_aemet[col] = df_aemet[col].replace('Ip', '0.0')
            df_aemet[col] = df_aemet[col].astype(str).str.replace(',', '.')
            df_aemet[col] = pd.to_numeric(df_aemet[col], errors='coerce')

    df_aemet = df_aemet.rename(columns={
        'tmed': 'T_media_C_AEMET', 'tmax': 'T_max_C_AEMET', 'tmin': 'T_min_C_AEMET',
        'prec': 'Precipitacio_mm_AEMET', 'sol': 'Hores_Sol_AEMET'
    })
    
    columnes_interes = ['T_media_C_AEMET', 'T_max_C_AEMET', 'T_min_C_AEMET', 
                        'Precipitacio_mm_AEMET', 'Hores_Sol_AEMET']
    df_aemet = df_aemet[df_aemet.columns.intersection(columnes_interes)]
    
    return df_aemet

def carregar_dades_era5():
    print("\n--- 2. Processant Dades ERA5 (GRIB) ---")
    
    try:
        import cfgrib
    except ImportError:
        print("ERROR: Falta 'cfgrib'.")
        return None

    arxius_inst = glob.glob(os.path.join(carpetaDatasets, '*_instantani.grib'))
    arxius_accum = glob.glob(os.path.join(carpetaDatasets, '*_acumulat.grib'))

    if not arxius_inst or not arxius_accum:
        print(f"ERROR: Falten arxius GRIB a {carpetaDatasets}")
        return None
        
    print(f"Processant {len(arxius_inst)} arxius instantanis i {len(arxius_accum)} acumulats...")

    try:
        # --- CANVI CLAU: combine='by_coords' ---
        # Això llegeix la data DINS del fitxer i ordena automàticament.
        
        print("Llegint dades instantànies (ordenant per data interna)...")
        ds_inst_hourly = xr.open_mfdataset(
            arxius_inst, 
            engine='cfgrib', 
            combine='by_coords',  # <--- AQUESTA ÉS LA SOLUCIÓ
            filter_by_keys={'typeOfLevel': 'surface'}
        )
        ds_inst_daily = ds_inst_hourly.resample(time='D').mean()

        print("Llegint dades acumulades (ordenant per data interna)...")
        ds_accum_hourly = xr.open_mfdataset(
            arxius_accum, 
            engine='cfgrib', 
            combine='by_coords', # <--- AQUESTA ÉS LA SOLUCIÓ
            filter_by_keys={'typeOfLevel': 'surface'}
        )
        ds_accum_daily = ds_accum_hourly.resample(time='D').sum()

    except Exception as e:
        print(f"ERROR CRÍTIC obrint GRIBs: {e}")
        print("Consell: Esborra tots els fitxers .idx de la carpeta i torna a provar.")
        return None

    # Unim i convertim
    ds_daily_total = xr.merge([ds_inst_daily, ds_accum_daily])
    ds_punt = ds_daily_total.isel(latitude=0, longitude=0)
    df_era5 = ds_punt.to_dataframe()
    
    # APLANAMENT DE L'ÍNDEX (Per si queda MultiIndex)
    if isinstance(df_era5.index, pd.MultiIndex):
        df_era5 = df_era5.reset_index()
        col_data = 'time' if 'time' in df_era5.columns else 'valid_time'
        if col_data in df_era5.columns:
            df_era5 = df_era5.set_index(col_data)
    
    print("Calculant variables derivades...")
    
    # Càlculs
    try:
        df_era5['Rn_MJ_dia'] = (df_era5['ssr'] - df_era5['str']) / 1_000_000
        df_era5['Vent_ms_ERA5'] = np.sqrt(df_era5['u10']**2 + df_era5['v10']**2)
        df_era5['Vent_2m_ms_ERA5'] = df_era5['Vent_ms_ERA5'] * 0.748
        
        T_k = df_era5['t2m']; Td_k = df_era5['d2m']
        T_c = T_k - 273.15; Td_c = Td_k - 273.15
        es = 0.61094 * np.exp((17.625 * T_c) / (T_c + 243.04))
        ea = 0.61094 * np.exp((17.625 * Td_c) / (Td_c + 243.04))
        df_era5['HR_media_ERA5'] = (ea / es) * 100
        df_era5['HR_media_ERA5'] = df_era5['HR_media_ERA5'].clip(0, 100)
        df_era5['T_media_C_ERA5'] = df_era5['t2m'] - 273.15

        return df_era5[['Rn_MJ_dia', 'Vent_2m_ms_ERA5', 'HR_media_ERA5', 'T_media_C_ERA5']]
        
    except KeyError as e:
        print(f"ERROR: Falta la variable {e}. Comprova la descàrrega.")
        return None

def main():
  

    print("Netejant arxius temporals .idx...")
    for f in glob.glob(os.path.join(carpetaDatasets, "*.idx")):
        os.remove(f)

    df_aemet = carregar_dades_aemet()
    if df_aemet is None: return

    df_era5 = carregar_dades_era5()
    if df_era5 is None: return
        
    print("\n--- 3. Unificant... ---")
    df_aemet.index = df_aemet.index.date
    df_era5.index = df_era5.index.date
    
    # Assegurem que no hi ha duplicats
    df_aemet = df_aemet[~df_aemet.index.duplicated(keep='first')]
    df_era5 = df_era5[~df_era5.index.duplicated(keep='first')]
    
    df_unificat = pd.concat([df_aemet, df_era5], axis=1)
    df_unificat.index = pd.to_datetime(df_unificat.index)
    df_unificat = df_unificat.asfreq('D')
    df_unificat = df_unificat.interpolate(method='time').fillna(method='bfill')

    #any_nom = "5" if "2025" in carpetaDatasets else "2024"
    arxiu_sortida = f'{carpetaDatasets}dades_unificades_{any_a_processar}.csv'
    df_unificat.to_csv(arxiu_sortida)

    print(f"\nÈXIT: Arxiu '{arxiu_sortida}' creat.")
    
    # AUDITORIA RÀPIDA
    print("\n--- AUDITORIA DE DADES (Comprova que té sentit) ---")
    # Agrupem per mes per veure si Gener té temperatura d'estiu
    df_unificat['mes'] = df_unificat.index.month
    resum = df_unificat.groupby('mes')[['T_media_C_ERA5', 'Rn_MJ_dia']].mean()
    print(resum)
    print("\nSi el Mes 1 (Gener) té Temp > 15ºC o Rn > 10, alguna cosa va malament.")

if __name__ == "__main__":
    main()
