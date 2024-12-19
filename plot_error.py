import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Percorso principale
base_dir = "/mnt/project_mnt/farm_fs/dmelegari/legget_garg/results_lg"

# Imposta un numero di shots come costante per la gestione degli errori
n_shots_values = [1000, 10000, 100000]
constant_errors = {shots: 1 / np.sqrt(shots) for shots in n_shots_values}

# Funzione principale per processare i file e generare i plot
def process_correlators(base_path):
    print(f"Starting to process {base_path}...")
    
    # Itera attraverso le sottocartelle di base_path (ad esempio, p_deco_0, p_deco_0.1, etc.)
    for p_deco_dir in os.listdir(base_path):
        p_deco_path = os.path.join(base_path, p_deco_dir)
        
        if os.path.isdir(p_deco_path):
            print(f"Processing {p_deco_dir}...")
            
            # Itera attraverso le cartelle per 100000_shots, 10000_shots, 1000_shots
            for shots_dir in os.listdir(p_deco_path):
                shots_path = os.path.join(p_deco_path, shots_dir)
                
                if os.path.isdir(shots_path) and "shots" in shots_dir:
                    print(f"Found shots directory: {shots_dir}")

                    # Verifica che ci sia una sottocartella 'correlators'
                    correlators_path = os.path.join(shots_path, "correlators")
                    if os.path.exists(correlators_path):
                        print(f"Found correlators in {correlators_path}")

                        # Estrai il numero di shots dal nome della cartella
                        try:
                            n_shots = int(shots_dir.split("_")[0])  # Estrae il numero di shots
                        except ValueError:
                            print(f"Skipping invalid shots folder: {shots_dir}")
                            continue
                        
                        constant_error = constant_errors.get(n_shots, None)
                        if constant_error is None:
                            print(f"No predefined error for {n_shots} shots. Skipping {shots_dir}.")
                            continue

                        # Pattern per i file CSV
                        file_pattern = os.path.join(correlators_path, "*.csv")
                        file_list = glob.glob(file_pattern)

                        # Aggiungi il debug per verificare i file trovati
                        print(f"File pattern: {file_pattern}")
                        print(f"Found {len(file_list)} CSV files in {correlators_path}.")  # Messaggio di debug

                        if len(file_list) == 0:
                            print(f"No CSV files found in {correlators_path}. Skipping.")  # Messaggio di debug

                        # Inizializzare un dizionario per raccogliere i valori
                        results = {}

                        # Leggere i file e raccogliere dati per ogni omega_tau
                        for file in file_list:
                            if os.stat(file).st_size == 0:
                                print(f"File {file} is empty. Skipping.")
                                continue
                            try:
                                df = pd.read_csv(file)
                                print(f"Reading {file}...")  # Messaggio di debug
                            except Exception as e:
                                print(f"Error reading {file}: {e}")
                                continue

                            for _, row in df.iterrows():
                                omega_tau = row['omega_tau']

                                K_3 = row['K_3']
                                    
                                if omega_tau not in results:
                                    results[omega_tau] = []
                                results[omega_tau].append(K_3)

                        # Calcolare la media e la deviazione standard per ogni omega_tau
                        omega_tau_values = []
                        mean_values = []
                        std_error_values = []

                        for omega_tau, K_3_values in sorted(results.items()):
                            omega_tau_values.append(omega_tau)
                            mean_values.append(np.mean(K_3_values))
                            std_error_values.append(np.sqrt(np.std(K_3_values)))

                        # Creare un DataFrame con i risultati
                        output_df = pd.DataFrame({
                            'omega_tau': omega_tau_values,
                            'mean_K_3': mean_values,
                            'std_error': std_error_values,
                            'constant_error': [constant_error] * len(omega_tau_values)
                        })

                        # Salva il file CSV nella cartella corrente
                        output_csv = os.path.join(shots_path, f"mean_and_error_values.csv")
                        output_df.to_csv(output_csv, index=False)
                        print(f"Results saved as CSV: {output_csv}")

                        # Creare il grafico
                        plt.figure(figsize=(10, 6))
                        plt.plot(omega_tau_values, mean_values, label='Mean of $K_3$', color='blue')

                        # Prima banda di errore (deviazione standard)
                        plt.fill_between(
                            omega_tau_values,
                            np.array(mean_values) - np.array(std_error_values),
                            np.array(mean_values) + np.array(std_error_values),
                            color='blue', alpha=0.2, label='Error band (std deviation)'
                        )

                        # Seconda banda di errore (errore costante)
                        plt.fill_between(
                            omega_tau_values,
                            np.array(mean_values) - constant_error,
                            np.array(mean_values) + constant_error,
                            color='orange', alpha=0.2, label='Error band (constant error)'
                        )

                        plt.xlabel('$\omega_\\tau$', fontsize=14)
                        plt.ylabel('Mean of $K_3$', fontsize=14)
                        plt.title(f'Mean of $K_3$ with Error Bands ({n_shots} shots)', fontsize=16)
                        plt.legend(fontsize=12)
                        plt.grid(alpha=0.3)
                        plt.tight_layout()

                        # Salva il grafico nella cartella {shots}_shots
                        output_plot_dir = shots_path  # Salva nella stessa cartella {shots}_shots
                        output_plot = os.path.join(output_plot_dir, f"K3_with_error_bands.png")
                        plt.savefig(output_plot, dpi=300)
                        plt.close()
                        print(f"Plot saved as: {output_plot}")

# Percorsi da processare
noise_path = os.path.join(base_dir, "results_lg_noise")
noiseless_path = os.path.join(base_dir, "results_lg_noiseless")

# Processa le due cartelle principali
process_correlators(noise_path)
process_correlators(noiseless_path)
