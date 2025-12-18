import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

# --- CONFIGURACIÓ AGRONÒMICA ---
KC_GESPA = 0.90          # Coeficient de cultiu (Gespa de parc)
EFICIENCIA_PLUJA = 0.75  # Aprofitem el 75% de l'aigua de pluja

# 1. Carreguem el cervell de la IA
print("Carregant el sistema d'IA (Model + Escalador)...")
try:
    model = joblib.load('model_et0_SVR.joblib')
    scaler = joblib.load('scaler_svr.joblib')
except FileNotFoundError:
    print("ERROR: No es troben els arxius .joblib. Has d'entrenar primer!")
    exit()

# 2. Carreguem dades històriques per a simular un dia real
# En un cas real, aquestes dades vindrien d'una API en temps real
df = pd.read_csv('DataSets2025/dades_amb_ET0_2025.csv', index_col=0, parse_dates=True)

# 3. Triem el dia de la prova: 15 de Juliol de 2025
dia_input = '2025-07-15'
dia_objectiu = '2025-07-16' # El dia per al qual volem decidir el reg

dades_ahir = df.loc[dia_input]
dades_avui = df.loc[dia_objectiu] # Necessitem saber si plou avui

print(f"\n--- 1. ANÀLISI DE SITUACIÓ ({dia_input}) ---")
print(f"Condicions atmosfèriques prèvies:")
print(f" - Temperatura: {dades_ahir['T_media_C_AEMET']:.1f} °C")
print(f" - Humitat:     {dades_ahir['HR_media_ERA5']:.1f} %")
print(f" - Radiació:    {dades_ahir['Rn_MJ_dia']:.1f} MJ/m2")

# 4. Preparem les dades per a la IA (Escalat)
dades_entrada = {
    'T_media_C_AEMET_ahir': [dades_ahir['T_media_C_AEMET']],
    'HR_media_ERA5_ahir':   [dades_ahir['HR_media_ERA5']],
    'Vent_2m_ms_ERA5_ahir': [dades_ahir['Vent_2m_ms_ERA5']],
    'Rn_MJ_dia_ahir':       [dades_ahir['Rn_MJ_dia']],
    'ET0_Calculada_ahir':   [dades_ahir['ET0_Calculada']]
}

df_input = pd.DataFrame(dades_entrada)
X_scaled = scaler.transform(df_input)

# 5. PREDICCIÓ DE PÈRDUA D'AIGUA (ET0)
et0_predita = model.predict(X_scaled)[0]
et0_final = max(0.0, et0_predita) # Corregim negatius

# 6. CÀLCUL DE LA NECESSITAT DE REG (El Balanç)
# Obtenim la pluja prevista/real per al dia objectiu
pluja_real = dades_avui['Precipitacio_mm_AEMET']
pluja_util = pluja_real * EFICIENCIA_PLUJA

# Fórmula: (Demanda) - (Aportació Natural)
demanda_planta = et0_final * KC_GESPA
deficit = demanda_planta - pluja_util

# Decisió final (mai reguem negatiu)
litres_reg = max(0.0, deficit)

print("-" * 40)
print(f"--- 2. RESULTAT DEL SISTEMA SMART ---")
print("-" * 40)
print(f"Evapotranspiració prevista (IA): {et0_final:.2f} mm")
print(f"Necessitat real gespa (Kc {KC_GESPA}):  {demanda_planta:.2f} mm")
print(f"Aportació Pluja ({pluja_real}mm x {EFICIENCIA_PLUJA}): -{pluja_util:.2f} mm")
print("-" * 40)

if litres_reg > 0:
    print(f"🚿 ORDRE ACTIVADA: REGAR {litres_reg:.2f} LITRES/m2")
else:
    print(f"🛑 ORDRE: NO REGAR (Estalvi d'aigua)")
print("-" * 40)

# Validació tècnica (opcional)
error = abs(et0_final - dades_avui['ET0_Calculada'])
print(f"(Nota tècnica: Error predicció vs Realitat: {error:.2f} mm)")
