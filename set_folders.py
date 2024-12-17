import os
import numpy as np

# Parametri configurabili
base_dir      = "/mnt/project_mnt/farm_fs/dmelegari/legget_garg"
shots_list    = ["1000", "10000", "100000"]  
theta         = np.pi/2
phi           = np.pi/2
p_deco        = 1
n_steps       = 1000
simulate      = True
noise         = False
n_simulations = 100

# Funzione per creare lo script bash in ogni cartella
def create_script(shots, folder_path, output_dir):
    script_name = os.path.join(folder_path, "run.sh")
    
    # Scrive lo script bash con i parametri corretti
    with open(script_name, "w") as f:
        f.write(f"""#!/bin/bash

# Deactivate any active virtual environment
deactivate 2>/dev/null || true

# Navigate to the project directory
cd {base_dir} || {{ echo 'Project directory not found'; exit 1; }}

# Activate the Python virtual environment
source env/bin/activate

# Check that the virtual environment is active
echo "Python path: $(which python3)"
echo "Python version: $(python3 --version)"
echo "Pip path: $(which pip3)"
pip3 show qiskit

# Add the main project directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:{os.path.dirname(base_dir)}

# Print PYTHONPATH for debugging
echo "PYTHONPATH: $PYTHONPATH"

# Run the main Python script with the provided parameters
echo 'Running main script...'
python3 {os.path.join(base_dir, "src/main.py")} {theta} {phi} {p_deco} {shots} {n_steps} {output_dir} {simulate} {noise} {n_simulations}
""")

    # Rende lo script eseguibile
    os.chmod(script_name, 0o755)
    print(f"Script creato per {shots} shots: {script_name}")

# Funzione per creare la .folder
def create_folder_file(folders_list):
    folder_file_path = os.path.join(base_dir, ".folder_0")
    
    # Scrive i percorsi delle cartelle in un file .folder
    with open(folder_file_path, "w") as f:
        for i, folder in enumerate(folders_list, start=1):
            f.write(f"{folder}, ")
    
    print(f".folder creato con i percorsi: {folder_file_path}")

# Funzione principale che crea le cartelle
def create_folders_and_scripts():
    folders_created = []  # Lista per tenere traccia delle cartelle create
    
    # Creazione delle cartelle e degli script
    for shots in shots_list:

        if noise == True:
            output_dir = os.path.join(base_dir, f"results_lg/results_lg_noise/p_deco_{p_deco}", f"{shots}_shots")  # Specifico per ogni valore di shots
        
        if noise == False:
            output_dir = os.path.join(base_dir, f"results_lg/results_lg_noiseless/p_deco_{p_deco}", f"{shots}_shots")  # Specifico per ogni valore di shots

        folder_path = output_dir
        
        # Crea la cartella per il numero di shots
        os.makedirs(folder_path, exist_ok=True)
        print(f"Cartella creata: {folder_path}")
        
        # Aggiungi la cartella alla lista
        folders_created.append(folder_path)
        
        # Crea lo script bash nella cartella
        create_script(shots, folder_path, output_dir)

    # Crea il file .folder con l'elenco delle cartelle
    create_folder_file(folders_created)

# Esegui la funzione di creazione cartelle e script
if __name__ == "__main__":
    create_folders_and_scripts()
    