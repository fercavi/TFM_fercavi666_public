import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- CONFIGURACIÓ DE RUTES (Basat en el teu script) ---
# Incloem tots els anys, inclòs el de validació
ANYS_TOTAL = range(2019, 2026) 
CARPETA_BASE = "DataSets" # Ajusta si la teua estructura és diferent

def carregar_dataset_total():
    """
    Llig i unifica tots els arxius CSV disponibles en un sol DataFrame.
    """
    print("--- 1. CARREGANT I UNIFICANT TOTES LES DADES ---")
    
    llista_dfs = []
    
    for any in ANYS_TOTAL:
        # Construïm la ruta seguint el patró del teu script
        # Exemple: DataSets2019/dades_amb_ET0_2019.csv
        carpeta_any = f"{CARPETA_BASE}{any}"
        arxiu = f"dades_amb_ET0_{any}.csv"
        ruta = os.path.join(carpeta_any, arxiu)

        if os.path.exists(ruta):
            print(f"Carregant {any}...")
            try:
                df_temp = pd.read_csv(ruta, index_col=0, parse_dates=True)
                # Afegim una columna 'Any' per facilitar l'anàlisi posterior
                df_temp['Any'] = any 
                llista_dfs.append(df_temp)
            except Exception as e:
                print(f"Error llegint l'arxiu {ruta}: {e}")
        else:
            print(f"⚠️ AVÍS: No s'ha trobat l'arxiu: {ruta}")

    if not llista_dfs:
        print("ERROR CRÍTIC: No s'han carregat dades.")
        return None

    # Unim tot en un gran DataFrame
    df_total = pd.concat(llista_dfs)
    print(f"\nÈXIT: Dataset total creat amb {len(df_total)} registres.")
    return df_total

def analisi_estadistic(df):
    """
    Genera estadístiques descriptives i guarda els resultats.
    """
    print("\n--- 2. ANÀLISI ESTADÍSTICA ---")
    
    # 1. Resum numèric
    descripcio = df.describe().T
    print("Resum estadístic:")
    print(descripcio)
    descripcio.to_csv('analisi_estadistic_resum.csv')
    print("-> Guardat a 'analisi_estadistic_resum.csv'")

    # 2. Correlacions (Mapa de calor)
    print("\nGenerant matriu de correlacions...")
    plt.figure(figsize=(10, 8))
    
    # Eliminem la columna 'Any' per a la correlació si no és rellevant
    cols_corr = [c for c in df.columns if c != 'Any']
    correlacio = df[cols_corr].corr()
    
    sns.heatmap(correlacio, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
    plt.title('Matriu de Correlació entre Variables')
    plt.tight_layout()
    plt.savefig('grafica_correlacions.png')
    print("-> Gràfica guardada a 'grafica_correlacions.png'")
    plt.show()

def analisi_distribucions(df):
    """
    Visualitza com es distribueixen les variables (Histogrames i Boxplots).
    """
    print("\n--- 3. ANÀLISI DE DISTRIBUCIONS ---")
    
    vars_interes = ['T_media_C_AEMET', 'HR_media_ERA5', 'Vent_2m_ms_ERA5', 'Rn_MJ_dia', 'ET0_Calculada']
    
    # 1. Histogrames
    df[vars_interes].hist(bins=30, figsize=(15, 10), layout=(2, 3), color='skyblue', edgecolor='black')
    plt.suptitle('Distribució de les Variables Principals', fontsize=16)
    plt.tight_layout()
    plt.savefig('grafica_histogrames.png')
    print("-> Gràfica guardada a 'grafica_histogrames.png'")
    plt.show()

    # 2. Boxplots per mes (Per veure l'estacionalitat)
    df['Mes'] = df.index.month
    
    fig, axes = plt.subplots(3, 2, figsize=(15, 15))
    axes = axes.flatten()
    
    for i, col in enumerate(vars_interes):
        sns.boxplot(x='Mes', y=col, data=df, ax=axes[i], palette='viridis')
        axes[i].set_title(f'Estacionalitat: {col}')
        axes[i].set_xlabel('Mes')
        axes[i].set_ylabel(col)
        
    # Esborrem l'últim gràfic buit si n'hi ha
    if len(vars_interes) < len(axes):
        fig.delaxes(axes[-1])

    plt.tight_layout()
    plt.savefig('grafica_boxplots_mensuals.png')
    print("-> Gràfica guardada a 'grafica_boxplots_mensuals.png'")
    plt.show()

def analisi_temporal(df):
    """
    Mostra l'evolució de l'ET0 al llarg de tots els anys.
    """
    print("\n--- 4. ANÀLISI TEMPORAL ---")
    
    plt.figure(figsize=(18, 6))
    plt.plot(df.index, df['ET0_Calculada'], label='ET0 Diària', color='orange', alpha=0.6, linewidth=1)
    
    # Mitjana mòbil per veure la tendència millor
    df['ET0_Mobil'] = df['ET0_Calculada'].rolling(window=30, center=True).mean()
    plt.plot(df.index, df['ET0_Mobil'], label='Mitjana Mòbil (30 dies)', color='red', linewidth=2)
    
    plt.title('Evolució de l\'Evapotranspiració (2019-2025)')
    plt.ylabel('ET0 (mm/dia)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('grafica_serie_temporal_total.png')
    print("-> Gràfica guardada a 'grafica_serie_temporal_total.png'")
    plt.show()

def main():
    # 1. Crear el dataset total
    df_total = carregar_dataset_total()
    
    if df_total is not None:
        # Guardem el dataset total per si el vols usar després
        df_total.to_csv('dataset_complet_2019_2025.csv')
        print("-> Dataset unificat guardat a 'dataset_complet_2019_2025.csv'")
        
        # 2. Executar anàlisis
        analisi_estadistic(df_total)
        analisi_distribucions(df_total)
        analisi_temporal(df_total)
        
        print("\nANÀLISI COMPLETAT.")

if __name__ == "__main__":
    main()
