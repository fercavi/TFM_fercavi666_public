import pandas as pd
import matplotlib.pyplot as plt
import sys

# 1. Carregar les dades
# Canvia 'ResultatsSVRGamma.csv' pel nom del teu fitxer
if len(sys.argv) < 2:
    print("Falta el nom de l'arxiu")
    sys.exit()

#nom_fitxer = 'ResultatsSVRGamma.csv'
nom_fitxer = sys.argv[1]

# Llegim el CSV indicant que el separador és ';' i assignem els noms a les columnes
df = pd.read_csv(nom_fitxer, sep=';', header=None, names=['i', 'R2', 'MAE', 'RMSE'])

# 2. Configuració de la gràfica
plt.figure(figsize=(12, 6)) # Mida de la imatge (amplada, alçada)

# 3. Dibuixar les tres línies
plt.plot(df['i'], df['R2'], label='R2 (Coef. Determinació)', color='blue', alpha=0.7)
plt.plot(df['i'], df['MAE'], label='MAE (Error Absolut Mitjà)', color='green', alpha=0.7)
plt.plot(df['i'], df['RMSE'], label='RMSE (Arrel Error Quadràtic Mitjà)', color='red', alpha=0.7)

# 4. Afegir detalls visuals
plt.title("Evolució de les mètriques d'error")
plt.xlabel("Iteració (i)")
plt.ylabel("Valor")
plt.legend() # Mostra la llegenda per identificar cada línia
plt.grid(True, linestyle='--', alpha=0.5) # Afegeix una quadrícula suau

# 5. Mostrar o guardar la gràfica
plt.savefig('resultat_grafica.png') # Guarda la imatge
plt.show() # Mostra la finestra amb la gràfica
