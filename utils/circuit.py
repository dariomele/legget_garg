import numpy as np
import os
import csv
from qiskit.circuit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from dotenv import load_dotenv

#==========================================================#
# 
# Quantum Circuit Utility Functions
#==========================================================#

def initial_state(qc: QuantumCircuit, 
                  sys: int, 
                  theta: float, 
                  phi: int):

    """
    Initialize the system qubit in a specific state.

    Args:
        qc (QuantumCircuit): Quantum circuit.
        sys (int): Index of the system qubit.
        theta (float): Rotation angle for the initial state.
        phi (float): Phase angle for the initial state.
    """
    
    qc.h(sys)
    qc.rz(theta, sys)
    qc.h(sys)
    qc.rz(phi, sys)

    return None


def apply_U(qc: QuantumCircuit, 
            sys: int, 
            omega_tau: float):

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
                     p_deco: float, 
                     basis: str):
    
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
    
    if basis == "x":
        qc.h(sys)
    
    qc.cx(env, sys)
    qc.rz(theta_deco, sys)
    qc.cx(env, sys)
    
    if basis == "x":
        qc.h(sys)

    return None




#==========================================================#
# 
# Calculation of the correlators
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
        apply_relaapply_relaxationxation(qc, sys, env[0], p_deco, basis="x")
        qc.measure(sys, 1)
        apply_U(qc, sys, omega_tau)
        (qc, sys, env[1], p_deco, basis="z")
    

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

    p00 = counts.get("00", 0)
    p01 = counts.get("01", 0)
    p10 = counts.get("10", 0)
    p11 = counts.get("11", 0)

    mean = (p00 + p11 - p01 - p10) / shots

    return mean

