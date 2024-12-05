#!/usr/bin/python3
"""
Quantum Circuit Builder for study the Legget-Garg inequalities, as described in arXiv:2109.02507
Author: Dario Melegari 
Date: 5rd December 2024

"""

import numpy as np
import os
from dotenv import load_dotenv
import csv

from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import U1Gate, U2Gate, U3Gate, CU3Gate, PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp, Kraus, SuperOp
from qiskit_aer import AerSimulator
from qiskit import transpile
from qiskit.providers import backend, fake_provider
from qiskit.visualization import plot_histogram
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2, Options
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.fake_provider import FakeBogotaV2  # fake backend

    # Import from Qiskit Aer noise module
from qiskit_aer.noise import (
    NoiseModel,
    QuantumError,
    ReadoutError,
    depolarizing_error,
    pauli_error,
    thermal_relaxation_error,
)


load_dotenv() # load the .env file in which is contained the IBM token


#==========================================================#
# 
# loading the backend on which to perform simulations
#==========================================================#

def load_backend(simulate, noise, min_num_qubits):
    
    if simulate == True:

        from qiskit_aer.aerprovider import AerSimulator
       
        if noise == True:

            noise_model = NoiseModel.from_backend(FakeBogotaV2())
            
            return AerSimulator(noise_model = noise_model)  
        
        
        elif noise == False:

            return AerSimulator()  

    
    elif simulate == False:
        from qiskit_ibm_runtime import QiskitRuntimeService
        service = QiskitRuntimeService()
        try:
            service = QiskitRuntimeService()
        except Exception as e:
            QiskitRuntimeService.save_account(channel="ibm_quantum", token=os.getenv("IBM_QUANTUM_API_TOKEN"), set_as_default=True)
        return service.least_busy(operational=True, simulator=False, min_num_qubits=min_num_qubits)


# For real quantum device with 10 qubit circuit
simulate = True
noise    = False

backend = load_backend(simulate, noise, 5)

print("Backend".center(50))
print("=" * 50)
print(f"{'Name:':<25} {backend.name}")
print(f"{'Status:':<25} {backend.status().to_dict()['status_msg']}")
print(f"{'Jobs:':<25} {backend.status().to_dict()['pending_jobs']}")
print(f"{'Available qubits:':<25} {backend.num_qubits}")
print("="*50, "\n")




#==========================================================#
# 
# Quantum Circuit Utility Functions
#==========================================================#

def initial_state(qc: QuantumCircuit,
                  sys: int, 
                  theta : float,
                  phi: float) -> None:
    """
    Initialize the system qubit in a specific state.

    Args:
        qc (QuantumCircuit): Quantum circuit.
        sys (int): Index of the system qubit.
        theta (float): Rotation angle for the initial state.
        phi (float): Phase angle for the initial state.
    """
    
    qc.h(sys)
    qc.append(U1Gate(theta), [sys])
    qc.h(sys)
    qc.append(U1Gate(phi + np.pi / 2), [sys])

    return None


def apply_U(qc: QuantumCircuit,
            sys: int, 
            omega_tau : float) -> None:
    """
    Apply exp(-i * omega * tau * X / 2) evolution.

    Args:
        qc (QuantumCircuit): Quantum circuit.
        sys (int): Index of the system qubit.
        omega_tau (float): Evolution parameter.
    """
    
    qc.h(sys)
    qc.rz(omega_tau, sys)
    qc.h(sys)

    return None


def apply_relaxation(qc: QuantumCircuit, 
                     sys: int, 
                     env: int, 
                     p_deco : float, 
                     basis="z") -> None:

    """
    Apply relaxation dynamics in a specified basis.

    Args:
        qc (QuantumCircuit): Quantum circuit.
        sys (int): Index of the system qubit.
        env (int): Index of the environment qubit.
        p_deco (float): Decoherence probability.
        basis (str): Basis of relaxation ('z' or 'x').
    """
    
    theta_deco = 2 * np.arccos(np.sqrt(1 - p_deco))
    cu3_gate = CU3Gate(theta_deco, 0, 0)

    if basis == "x":
        qc.h(sys)

    qc.cx(env, sys)
    qc.append(cu3_gate, [sys, env])
    qc.cx(env, sys)

    if basis == "x":
        qc.h(sys)

    return None 


#==========================================================#
# 
# Correlator Calculation Functions
#==========================================================#

def calculate_correlator(qc: QuantumCircuit, 
                         sys: int, 
                         env: int, 
                         theta: float, 
                         phi: float, 
                         omega_tau: float,
                         p_deco: float, 
                         shots: int, 
                         sequence: str,
                         backend) -> None:
    """
    General correlator calculation based on a specified sequence.

    Args:
        qc (QuantumCircuit): Quantum circuit.
        sys (int): System qubit index.
        env (list): Environment qubits indices.
        theta (float): Initial state parameter.
        phi (float): Initial state parameter.
        omega_tau (float): Evolution parameter.
        p_deco (float): Decoherence probability.
        shots (int): Number of measurement shots.
        sequence (str): Measurement and evolution sequence ("C_12", "C_13", "C_23").

    Returns:
        float: Correlator mean value.
    """
    
    initial_state(qc, sys, theta, phi)

    if sequence == "C_12":
        
        qc.measure(sys, 0)
        apply_U(qc, sys, omega_tau)
        apply_relaxation(qc, sys, env[0], p_deco, basis="x")
        qc.measure(sys, 1)
        apply_U(qc, sys, omega_tau)
        apply_relaxation(qc, sys, env[1], p_deco, basis="z")
    

    elif sequence == "C_13":
        
        qc.measure(sys, 0)
        apply_U(qc, sys, omega_tau)
        apply_relaxation(qc, sys, env[0], p_deco, basis="x")
        apply_U(qc, sys, omega_tau)
        apply_relaxation(qc, sys, env[1], p_deco, basis="z")
        qc.measure(sys, 1)
    

    elif sequence == "C_23":
        
        apply_U(qc, sys, omega_tau)
        apply_relaxation(qc, sys, env[0], p_deco, basis="x")
        qc.measure(sys, 0)
        apply_U(qc, sys, omega_tau)
        apply_relaxation(qc, sys, env[1], p_deco, basis="z")
        qc.measure(sys, 1)


    result = backend.run(qc, shots=shots).result()
    counts = result.get_counts()
    
    p00 = counts.get('00', 0)
    p01 = counts.get('01', 0)
    p10 = counts.get('10', 0)
    p11 = counts.get('11', 0)

    mean = (p00 + p11 - p01 - p10) / shots

    return mean



#==========================================================#
#
#  Main Execution
#==========================================================#

if __name__ == "__main__":
    
    simulate = True
    noise    = False
    
    backend = load_backend(simulate, noise, min_num_qubits = 5)

    n_qubits    = 3
    sys         = 0
    env         = [1, 2]
    n_classical = 2
    
    
    #
    # Circuit parameters
    #----------------------------------------------------------#

    theta  = 0.7
    phi    = 1.2
    p_deco = 0
    
    shots = 1e6
    
    sequences = ["C_12", "C_13", "C_23"]

    n_steps = 100
    omega_tau_values = [0.4] # np.linspace(0, 2 * np.pi, n_steps)

    results = []

    if noise == False:
        output_file = "correlators_results_noiseless.csv"

    elif noise == True:
        output_file = "correlators_results_noisy.csv"
    

    with open(output_file, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["omega_tau", "C_12", "C_13", "C_23", "K_3"])

        for omega_tau in omega_tau_values:
            correlators = []
            for seq in sequences:
                
                qc = QuantumCircuit(n_qubits, n_classical)
                
                mean = calculate_correlator(qc, sys, env, theta, phi, omega_tau, p_deco, shots, seq, backend)

                correlators.append(mean)

            C_12 = correlators[0]
            C_13 = correlators[1]
            C_23 = correlators[2]

            K_3 = C_12 + C_23 - C_13

            results.append([omega_tau, *correlators, K_3])
            writer.writerow([omega_tau, *correlators, K_3])

            print(omega_tau)

    print(f"Results saved to {output_file}")
