import xarray as xr
import sys
import os

# --- Paràmetres ---
ANY = "2024"
MES = "01"

nom_inst = f"{ANY}{MES}_era5_instantani.grib"
nom_accum = f"{ANY}{MES}_era5_acumulat.grib"

print(f"--- Obrint fitxers: {nom_inst} i {nom_accum} ---")

try:
    # 1. Obrim els dos fitxers per separat
    ds_inst = xr.open_dataset(nom_inst, engine='cfgrib')
    ds_accum = xr.open_dataset(nom_accum, engine='cfgrib')

    print("\n--- Fitxer Instantani (t2m, d2m, u10, v10) ---")
    print(ds_inst)
    
    print("\n--- Fitxer Acumulat (ssr, str) ---")
    print(ds_accum)

    # 2. Eliminem coordenades extra que poden donar conflictes en fusionar
    #    (com 'step', 'valid_time', etc., que no són iguals en ambdós fitxers)
    #    Deixem només les coordenades principals: time, latitude, longitude.
    
    # Llista de coordenades a mantenir
    coords_a_mantenir = ['time', 'latitude', 'longitude']
    
    # Filtrem les variables de coordenades que no volem
    vars_a_eliminar_inst = [v for v in ds_inst.coords if v not in coords_a_mantenir]
    vars_a_eliminar_accum = [v for v in ds_accum.coords if v not in coords_a_mantenir]
    
    ds_inst = ds_inst.drop_vars(vars_a_eliminar_inst)
    ds_accum = ds_accum.drop_vars(vars_a_eliminar_accum)

    # 3. Fusionem els dos Datasets
    #    xr.merge alinearà els dos datasets usant les coordenades idèntiques.
    print("\n--- Fusionant els dos Datasets... ---")
    ds_complet = xr.merge([ds_inst, ds_accum])

    # 4. Imprimim el resultat final
    print("\n--- RESULTAT: Dataset Combinat ---")
    print(ds_complet)
    
    print("\n--- Variables presents al dataset final: ---")
    for var in ds_complet.data_vars:
        print(f"- {var}")

except FileNotFoundError as e:
    print(f"\nERROR: No s'ha trobat l'arxiu: {e.filename}")
    print("Assegura't d'haver descarregat els fitxers amb l'script 'baixarERA5.py' modificat.")
except Exception as e:
    print(f"\nS'ha produït un error en obrir o fusionar els arxius GRIB: {e}")
