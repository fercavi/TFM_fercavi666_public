import joblib
:
model.fit(X_train, Y_train)
print("Model entrenat!")

# --- GUARDAR EL MODEL ---
nom_arxiu_model = 'model_et0_random_forest.joblib'
joblib.dump(model, nom_arxiu_model)
print(f"Model guardat exitosament al disc: {nom_arxiu_model}")
