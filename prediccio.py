import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler


# 1. Carreguem el model que vam guardar
print("Carregant el cervell de la IA...")
model = joblib.load('model_et0_SVR.joblib')

scaler = joblib.load('scaler_svr.joblib')

# 2. Arriben dades noves (per exemple, via petició HTTP)
# Dades d'ahir: [Temp, Humitat, Vent, Radiació, ET0_ahir]
df = pd.read_csv('DataSets2025/dades_amb_ET0_2025.csv', index_col=0, parse_dates=True)
# 3. Triem un dia concret: El 15 de Juliol de 2025 (Estiu pur)
dia_triat = '2025-07-15'
dades_reals = df.loc[dia_triat]
print(f"\n--- PROVA AMB DADES REALS DEL {dia_triat} ---")
print(f"Dades d'entrada (Ahir):")
print(f" - Temp: {dades_reals['T_media_C_AEMET']:.1f} C")
print(f" - Humitat: {dades_reals['HR_media_ERA5']:.1f} %")
print(f" - Vent: {dades_reals['Vent_2m_ms_ERA5']:.1f} m/s")
print(f" - Radiació: {dades_reals['Rn_MJ_dia']:.1f} MJ/m2")


# 4. Preparem el diccionari amb els noms correctes (acabats en _ahir)
dades_entrada = {
    'T_media_C_AEMET_ahir': [dades_reals['T_media_C_AEMET']],
    'HR_media_ERA5_ahir':   [dades_reals['HR_media_ERA5']],
    'Vent_2m_ms_ERA5_ahir': [dades_reals['Vent_2m_ms_ERA5']],
    'Rn_MJ_dia_ahir':       [dades_reals['Rn_MJ_dia']],
    'ET0_Calculada_ahir':   [dades_reals['ET0_Calculada']]
}

df_input = pd.DataFrame(dades_entrada)
df_input = scaler.transform(df_input)

# 5. Predicció
prediccio_bruta = model.predict(df_input)[0]
prediccio_final = max(0.0, prediccio_bruta)

print(f"\nPREDICCIÓ PER A L'ENDEMÀ ({prediccio_final:.2f} mm)")
print("-" * 30)

# Comprovem què va passar realment l'endemà (16 de Juliol)
dia_seguent = '2025-07-16'
realitat = df.loc[dia_seguent]['ET0_Calculada']
print(f"Realitat del dia següent: {realitat:.2f} mm")
print(f"Error: {abs(prediccio_final - realitat):.2f} mm")
