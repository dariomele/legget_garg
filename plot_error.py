import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

n_shots = 10000
constant_error = 1 / np.sqrt(n_shots)

# Percorso ai file CSV
file_pattern = f"/mnt/project_mnt/farm_fs/dmelegari/legget_garg/results_lg/results_lg_noiseless/p_deco_0/{n_shots}_shots/correlators_results_*_noiseless.csv"
file_list = glob.glob(file_pattern)

# Inizializzare un dizionario per raccogliere i valori
results = {}

# Leggere i file e raccogliere dati per ogni omega_tau
for file in file_list:
    if os.stat(file).st_size == 0:
        print(f"File {file} is empty. Skipping.")
        continue
    try:
        df = pd.read_csv(file)
    except pd.errors.EmptyDataError:
        print(f"File {file} is empty or invalid. Skipping.")
        continue
    except Exception as e:
        print(f"An error occurred while reading {file}: {e}")
        continue

    for _, row in df.iterrows():
        omega_tau = row['omega_tau']
        K_3 = row['K_3']
        if omega_tau not in results:
            results[omega_tau] = []
        results[omega_tau].append(K_3)

# Calcolare la media e la radice della deviazione standard per ogni omega_tau
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

# Percorso per salvare il file CSV
output_dir = os.path.dirname(file_pattern)
output_csv = os.path.join(output_dir, "mean_and_error_values.csv")
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

plt.xlabel('$\omega_\tau$', fontsize=14)
plt.ylabel('Mean of $K_3$', fontsize=14)
plt.title('Mean of $K_3$ with Error Bands', fontsize=16)
plt.legend(fontsize=12)
plt.grid(alpha=0.3)
plt.tight_layout()

# Salva il grafico come PNG
output_plot = os.path.join(output_dir, "K3_with_error_bands.png")
plt.savefig(output_plot, dpi=300)

print(f"Plot saved as: {output_plot}")
