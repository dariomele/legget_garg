import numpy as np
import sys, os
import csv
from qiskit.circuit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from dotenv import load_dotenv


sys.path.append('/mnt/project_mnt/farm_fs/dmelegari/legget_garg/') 

from utils.backend import load_backend
from utils.config  import print_runcard
from utils.circuit import *


#==========================================================#
# 
# Run the circuit
#==========================================================#

def run_simulation(theta: float, 
                   phi: float, 
                   p_deco: float, 
                   shots: int, 
                   n_steps : int,
                   output_dir,
                   simulation_id : int,
                   simulate,
                   noise) -> None:
    
    #
    # Circuit settings
    #----------------------------------------------------------#

    n_qubits = 3     # number of qubits (1 sys, 2 env)
    n_classical = 2  # number of classical bits
    sys = 0          # sys qubit index  
    env = [1, 2]     # env qubits indeces

    sequences = ["C_12", "C_13", "C_23"]
    
    omega_tau_values = np.linspace(0, 2 * np.pi, n_steps)

    print(noise)

    backend = load_backend(simulate, noise, min_num_qubits=5)


    # print_runcard here before running the simulation
    print_runcard(
        output_dir,
        p_deco=p_deco,
        n_qubits=n_qubits,
        theta=theta,
        phi=phi,
        shots=shots,
        sequences=sequences,
        n_steps=n_steps
    )

    # Define the output file based on the noise condition
    if noise:
        output_file = os.path.join(output_dir, f"correlators_results_{simulation_id}_noise.csv")
    else:
        output_file = os.path.join(output_dir, f"correlators_results_{simulation_id}_noiseless.csv")

    with open(output_file, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["omega_tau", "C_12", "C_13", "C_23", "K_3"])

        for omega_tau in omega_tau_values:
            correlators = []
            for seq in sequences:
                qc = QuantumCircuit(n_qubits, n_classical)
                mean = calculate_correlator(qc, sys, env, theta, phi, omega_tau, p_deco, shots, seq, backend)
                correlators.append(mean)    

            C_12, C_13, C_23 = correlators
            K_3 = C_12 + C_23 - C_13

            writer.writerow([omega_tau, *correlators, K_3])

#==========================================================#
#
#  Main Execution
#==========================================================#

if __name__ == "__main__":
    
    theta         = float(sys.argv[1])
    phi           = float(sys.argv[2])
    p_deco        = float(sys.argv[3])
    n_shots       = int(sys.argv[4])
    n_steps       = int(sys.argv[5])
    output_dir    = sys.argv[6]
    simulate      = sys.argv[7].lower() == "true"  # Converti 0/1 o true/false in un booleano
    noise         = sys.argv[8].lower() == "true" # Converti 0/1 o true/false in un booleano
    n_simulations = int(sys.argv[9])

    print(noise)

    for simulation_id in range(1, n_simulations + 1):  # Execute N simulations
        run_simulation(theta, phi, p_deco, n_shots, n_steps, output_dir, simulation_id, simulate, noise)
        print(f"Done simulation {simulation_id}")
