import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor,GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import os
import sys

# --- CONFIGURACIÓ DE RUTES ---
#ARXIU_TRAIN = 'DataSets2024/dades_amb_ET0_2024.csv'      # Dades per entrenar
ANYS_TRAIN = range(2019, 2025)
ARXIU_TEST  = 'DataSets2025/dades_amb_ET0_2025.csv'  # Dades per validar (futur)
# --- Paràmetres ---
if len(sys.argv) < 4:
    print("❌ Error: No has passat el rang de estimadors, o el regressor")
    print("Ús: python el_teu_script.py minim maxim regressor")
    sys.exit()  # Això tanca el programa immediatament

# 2. Capturem el paràmetre
rang_minim = int(sys.argv[1])
rang_maxim = int(sys.argv[2])
regressorPar = int(sys.argv[3])




def preparar_dades(df):
    """
    Genera les variables d'entrada (lags) necessàries per al model.
    La IA no pot veure el futur, així que li donem les dades d'ahir (t-1).
    """
    df_processat = df.copy()
    
    # Variables que utilitzarem com a predictors
    features_base = [
        'T_media_C_AEMET', 
        'HR_media_ERA5', 
        'Vent_2m_ms_ERA5', 
        'Rn_MJ_dia', 
        'ET0_Calculada'
    ]
    
    # Creem els retards (Lags): Dades d'ahir (t-1) i d'abans d'ahir (t-2)
    for col in features_base:
        df_processat[f'{col}_ahir'] = df_processat[col].shift(1)
        # Opcional: Podeu descomentar la línia següent per afegir més context (t-2)
        # df_processat[f'{col}_abans_ahir'] = df_processat[col].shift(2)
        
    # Eliminem les primeres files que ara tenen NaNs (perquè no tenen "ahir")
    return df_processat.dropna()

def main():
    #print("--- 1. CARREGANT DADES ---")
    
    # Comprovem que els arxius existeixen
    #if not os.path.exists(ARXIU_TRAIN) or not os.path.exists(ARXIU_TEST):
    #    print("ERROR: No es troben els arxius CSV.")
    #    print(f"Cercant a: {ARXIU_TRAIN} i {ARXIU_TEST}")
    #    return

    # Carreguem els CSV
    #df_2024 = pd.read_csv(ARXIU_TRAIN, index_col=0, parse_dates=True)
    llista_dfs = []
    for any in ANYS_TRAIN:
        # Construïm la ruta dinàmicament: Ex: DataSets2019/dades_amb_ET0_2019.csv
        ruta = f"DataSets{any}/dades_amb_ET0_{any}.csv"

        if os.path.exists(ruta):
            #print(f"Carregant any {any}...")
            df_temp = pd.read_csv(ruta, index_col=0, parse_dates=True)
            llista_dfs.append(df_temp)
        else:
            print(f"⚠️ ATENCIÓ: No s'ha trobat l'arxiu per a l'any {any} a: {ruta}")

    # Unim tots els anys en un sol DataFrame gran
    if llista_dfs:
        df_train_total = pd.concat(llista_dfs)
        #print(f"Total dades entrenament carregades: {len(df_train_total)} dies.")
    else:
        print("ERROR CRÍTIC: No s'ha carregat cap dada d'entrenament.")
        return
    df_2025 = pd.read_csv(ARXIU_TEST, index_col=0, parse_dates=True)
    
    #print(f"Dades 2024 carregades: {len(df_2024)} dies.")
    #print(f"Dades 2025 carregades: {len(df_2025)} dies.")

    #print("\n--- 2. ENGINYERIA DE CARACTERÍSTIQUES (Feature Engineering) ---")
    
    # Preparem els dos conjunts de dades amb la mateixa funció
    #train_data = preparar_dades(df_2024)
    train_data = preparar_dades(df_train_total)
    test_data = preparar_dades(df_2025)
    
    # Definim X (Variables explicatives - El Passat) i Y (Objectiu - El Present)
    # Seleccionem només les columnes que acaben en '_ahir'
    cols_input = [c for c in train_data.columns if '_ahir' in c]
    target = 'ET0_Calculada'
    
    X_train = train_data[cols_input]
    Y_train = train_data[target]
    
    X_test = test_data[cols_input]
    Y_test = test_data[target]
    
    #print(f"Variables utilitzades per a predir (Inputs):")
    #for col in cols_input:
    #    print(f" - {col}")

    #print("\n--- 3. ENTRENAMENT DEL MODEL (Random Forest) ---")
    
    # Instanciem i entrenem el model
    # n_estimators=100: Crea 100 arbres de decisió
    # random_state=42: Per a què els resultats siguen reproduïbles
    for i in range(rang_minim, rang_maxim + 1):
        #model = RandomForestRegressor(n_estimators=i, random_state=42, max_depth=10000000)        
        if  (regressorPar == 1):
            model = RandomForestRegressor(n_estimators=i, random_state=42, max_depth=10)
        elif(regressorPar == 2):
            model = LinearRegression()
        elif(regressorPar == 3):
            model = DecisionTreeRegressor(random_state=42, max_depth=10)
        elif(regressorPar == 4):
            model = GradientBoostingRegressor(random_state=42)
        elif(regressorPar == 5):
            
            model = SVR(gamma=1/200, epsilon=i*0.001)
        elif(regressorPar == 6):
            model = KNeighborsRegressor()
        else:
            model = None
        #model = regressor(n_estimators=i, random_state=42, max_depth=10)
    
        model.fit(X_train, Y_train)
    

        #print("\n--- 4. VALIDACIÓ AMB DADES NOVES (2025) ---")
    
    # Fem la predicció sobre el 2025
        prediccions = model.predict(X_test)
    
    # Calculem mètriques d'error
        rmse = np.sqrt(mean_squared_error(Y_test, prediccions))
        mae = mean_absolute_error(Y_test, prediccions)
        r2 = r2_score(Y_test, prediccions)
    
    #print("-" * 30)
    #print(f"RESULTATS DE LA VALIDACIÓ (ANY 2025):")
    #print("-" * 30)
    #print(f"RMSE (Error Quadràtic Mitjà): {rmse:.4f} mm/dia")
    #print(f"MAE  (Error Absolut Mitjà):   {mae:.4f} mm/dia")
    #print(f"R²   (Coeficient de Determinació): {r2:.4f} (Més prop d'1 és millor)")
        #print(f"{i};{r2:.4f};{mae:.4f};{rmse:.4f}")
        print(r"\begin{itemize}")
        print(f"    \item $R^2 = {r2:.4f}$")
        print(f"    \item $MAE = {mae:.4f}$")
        print(f"    \item $RMSE = {rmse:.4f}$")
        print(r"\end{itemize}")

    #print("-" * 30)
# --- 5. GENERACIÓ DE GRÀFIQUES COMPLETES (2019-2025) ---
    #print("\nGenerant gràfica de la sèrie temporal completa...")
    
    # 1. Predicció sobre l'entrenament (per veure l'ajust històric)
        prediccions_train = model.predict(X_train)
    
    # 2. Unim les dades reals (Tot l'històric)
    # Això crearà la línia BLAVA contínua de 2019 a 2025
        Y_total = pd.concat([Y_train, Y_test])
    
    # 3. Unim les prediccions (Ajust + Futur)
    # Això crearà la línia ROJA contínua
        prediccions_total = np.concatenate([prediccions_train, prediccions])
        series_prediccions = pd.Series(prediccions_total, index=Y_total.index)

    # Configurar la gràfica gran
    #plt.figure(figsize=(18, 8))
    
    # Dibuixar Realitat (Blau)
    #plt.plot(Y_total.index, Y_total.values, label='ET0 Real (Càlcul Físic)', color='#1f77b4', alpha=0.6, linewidth=1)
    
    # Dibuixar Model (Roig)
    #plt.plot(series_prediccions.index, series_prediccions.values, label='Model IA (Ajust i Predicció)', color='#d62728', alpha=0.8, linewidth=1)
    
    # Dibuixar línia vertical per separar Entrenament de Validació
    # El punt de tall és l'últim dia de X_train (final de 2024)
    #plt.axvline(x=X_train.index[-1], color='black', linestyle='--', linewidth=2, label='Inici Validació (2025)')
    
    #plt.title(f'Evolució Històrica i Validació: Model entrenat amb {len(ANYS_TRAIN)} anys vs 2025', fontsize=16)
    #plt.ylabel('Evapotranspiració (mm/dia)', fontsize=12)
    #plt.xlabel('Any', fontsize=12)
    #plt.legend(fontsize=12, loc='upper right')
    #plt.grid(True, alpha=0.3)
    
    # Guardem
    #fitxer_grafica = 'img/resultat_serie_completa_2019-2025.png'
    #plt.savefig(fitxer_grafica, dpi=300)
    #print(f"Gràfica completa guardada com a: {fitxer_grafica}")
    
    # Mostrem la importància de les variables
    #importancies = pd.Series(model.feature_importances_, index=cols_input).sort_values(ascending=False)
    #print("\nImportància de les variables:")
    #print(importancies)

    #plt.show()

if __name__ == "__main__":
    main()
