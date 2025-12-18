import requests
import json
import sys
# 1. La teua clau (API Key)
api_key = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmZXJjYXZpNjY2QHVvYy5lZHUiLCJqdGkiOiIzYzQ0OWJmYy03ZGI1LTRjYzEtYWY5Mi02MGJiNzM3MmYxOWMiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTc2Mjg1MTAxNywidXNlcklkIjoiM2M0NDliZmMtN2RiNS00Y2MxLWFmOTItNjBiYjczNzJmMTljIiwicm9sZSI6IiJ9.MLrOc5sw6sPMKJluEXCrZPbr7959Jt6pZMG-ydpv6bY" # Posa ací la clau que has obtingut

# 2. La URL de l'endpoint que vols (Exemple: dades diàries de València)
# AQUESTA URL L'HAS DE BUSCAR A LA DOCUMENTACIÓ DE L'API
# Per exemple, per a dades diàries, l'endpoint és:
# /api/valores/climatologicos/diarios/datos/fechaini/{fechaini}/fechafin/{fechafin}/estacion/{estacion}

# Dades per a l'estació de València (8416) per a un dia
if len(sys.argv) < 2:
    print("❌ Error: No has passat cap any.")
    print("Ús: python el_teu_script.py <ANY>")
    sys.exit()  # Això tanca el programa immediatament
parametre = sys.argv[1]
any_a_processar = int(parametre);
url_diariaA = f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{any_a_processar}-01-01T00:00:00UTC/fechafin/{any_a_processar}-06-31T23:59:59UTC/estacion/8416"
url_diariaB = f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{any_a_processar}-07-01T00:00:00UTC/fechafin/{any_a_processar}-12-31T23:59:59UTC/estacion/8416"

# 3. Capçalera (Header) amb la teua API Key
headers = {
    'api_key': api_key,
    'Accept': 'application/json'
}

# 4. Primera petició (GET)
def processar(url_diaria,nom_arxiu):
    try:
        response_inicial = requests.get(url_diaria, headers=headers)
        response_inicial.raise_for_status() # Controla errors HTTP (4xx, 5xx)
    
    # 5. Obtenir la URL de les dades
        dades_resposta = response_inicial.json()
    
        if dades_resposta['estado'] == 200:
            url_dades_finals = dades_resposta['datos']
        
        # 6. Segona petició (GET) per a les dades finals
            response_final = requests.get(url_dades_finals)
            response_final.raise_for_status()
        
        # Aquestes són les teues dades!
            dades_climatiques = response_final.json()
        
            print("Dades obtingudes amb èxit:")
            #print(json.dumps(dades_climatiques, indent=4, ensure_ascii=False))
            with open(nom_arxiu, "w", encoding="utf-8") as fitxer:
                json.dump(dades_climatiques, fitxer, indent=4, ensure_ascii=False)

        else:
            print(f"Error en la petició inicial: {dades_resposta['descripcion']}")

    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de Connexió: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Error de Timeout: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
    except KeyError:
        print("Error: No s'ha pogut trobar la URL de 'datos' a la resposta.")
        print("Resposta rebuda:", dades_resposta)
nom_arxiu = f"DataSets{any_a_processar}/{any_a_processar}AemetA.json"
processar(url_diariaA,nom_arxiu)
nom_arxiu = f"DataSets{any_a_processar}/{any_a_processar}AemetB.json"
processar(url_diariaB,nom_arxiu)
