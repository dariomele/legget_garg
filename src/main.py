#!/usr/bin/python3
"""
Quantum Circuit Builder for QNDM Systems
Author: Dario Melegari 
Date: 21th October 2024

This script defines a quantum circuit with trotterized evolution, system initialization, 
and interaction dynamics, including relaxation effects in different bases.
"""

from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import U1Gate, U2Gate, CU3Gate, PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp
import numpy as np
from qiskit.providers import backend
from qiskit_aer.noise import NoiseModel
from qiskit_aer import AerSimulator
from qiskit import transpile

from qiskit.providers import fake_provider
from qiskit_aer.noise import NoiseModel
from qiskit.providers.fake_provider import Fake5QV1

from qiskit_ibm_runtime import SamplerV2, Options
from qiskit.providers.models import BackendProperties


# Flag per abilitare o disabilitare il rumore
noise = True

# Usa un backend finto come Fake5QV1
fake_backend = Fake5QV1()

# Configura un modello di rumore dal backend finto
if noise:
    noise_model = NoiseModel.from_backend(fake_backend)
else:
    noise_model = None

# Configura SamplerV2 con il backend finto
options = Options(resilience_level=1)  # Livello di resilienza per gestire errori
fake_sampler = SamplerV2(backend=fake_backend, options=options)



'''




# ==========================================================#
# Configuration and Utility Functions
# ==========================================================#

def initialize_system(qc: QuantumCircuit, sys: QuantumRegister, theta: float, phi: float) -> None:
    """
    Initialize the system qubits in a specific state.

    Args:
        qc (QuantumCircuit): The quantum circuit.
        sys (QuantumRegister): System qubits.
        theta (float): Rotation parameter for the U1 gate.
        phi (float): Phase parameter for the U1 gate.
    """
    qc.h(sys)      
    qc.append(U1Gate(theta), sys)
    qc.h(sys)
    qc.append(U1Gate(phi + np.pi / 2), sys)


def apply_trotterized_evolution(qc: QuantumCircuit, Lambda: float, HP: SparsePauliOp, sys_det: list) -> None:
    """
    Apply the operator exp(i * Lambda / 2 * H * P) using a trotterized evolution.

    Args:
        qc (QuantumCircuit): The quantum circuit.
        Lambda (float): Evolution parameter.
        HP (SparsePauliOp): Interaction operator.
        sys_det (list): List of qubits affected by the operator.
    """
    trotterized_op = PauliEvolutionGate(HP, Lambda)
    qc.append(trotterized_op, sys_det)


def apply_relaxation_z(qc: QuantumCircuit, sys: QuantumRegister, env: QuantumRegister, p_deco: float) -> None:
    """
    Apply relaxation dynamics in the Z basis.

    Args:
        qc (QuantumCircuit): The quantum circuit.
        sys (QuantumRegister): System qubit.
        env (QuantumRegister): Environment qubit.
        p_deco (float): Decoherence probability.
    """
    theta_deco = 2 * np.arccos(np.sqrt(1 - p_deco))
    cu3_gate = CU3Gate(theta_deco, 0, 0)
    
    qc.cx(env, sys)
    qc.append(cu3_gate, [env, sys])
    qc.cx(env, sys)


def apply_relaxation_x(qc: QuantumCircuit, sys: QuantumRegister, env: QuantumRegister, p_deco: float) -> None:
    """
    Apply relaxation dynamics in the X basis.

    Args:
        qc (QuantumCircuit): The quantum circuit.
        sys (QuantumRegister): System qubit.
        env (QuantumRegister): Environment qubit.
        p_deco (float): Decoherence probability.
    """
    theta_deco = 2 * np.arccos(np.sqrt(1 - p_deco))
    cu3_gate = CU3Gate(theta_deco, 0, 0)
    
    qc.h(sys)
    qc.cx(env, sys)
    qc.append(cu3_gate, [env, sys])
    qc.cx(env, sys)
    qc.h(sys)


#==========================================================#
# 
# Circuit Construction
#==========================================================#

def build_circuit(qc: QuantumCircuit, sys: QuantumRegister, det: QuantumRegister, env: QuantumRegister, 
                  theta: float, phi: float, p_deco: float, flag: str) -> None:
    """
    Build the quantum circuit with the specified components.

    Args:
        qc (QuantumCircuit): The quantum circuit.
        sys (QuantumRegister): System qubits.
        det (QuantumRegister): Detector qubits.
        env (QuantumRegister): Environment qubits.
        theta (float): Initial state parameter.
        phi (float): Initial state phase.
        p_deco (float): Decoherence probability.
        flag (str): Specifies measurement basis ('real' or 'imag').
    """
    initialize_system(qc, sys, theta, phi)
    qc.h(det)

    # Interaction with the detector and environment
    apply_trotterized_evolution(qc, Lambda, HP_op, sys[:] + det[:])
    qc.x(sys)
    apply_relaxation_z(qc, sys, env[0], p_deco)
    apply_trotterized_evolution(qc, Lambda, HP_op, sys[:] + det[:])
    qc.x(sys)
    apply_trotterized_evolution(qc, Lambda, HP_op, sys[:] + det[:])
    apply_relaxation_x(qc, sys, env[1], p_deco)

    # Measurement basis
    if flag == "real":
        qc.h(det)
    elif flag == "imag":
        qc.append(U2Gate(np.pi / 2, -np.pi / 2), det)
    else:
        raise ValueError("Invalid flag value. Use 'real' or 'imag'.")

    qc.barrier()

    qc.measure(det, 0)


    # Transpile the circuit
    qc_transpiled = transpile(qc, simulator)
    sim_result = simulator.run(qc_transpiled, shots=shots).result()
    data = sim_result.get_counts(qc)

    p0, p1 = 0, 0
    # extract counts
    for l in data.keys():
        if l == '0':
            p0 += data[l] / shots  # probability of |0> in the detector state
        elif l == '1':
            p1 += data[l] / shots  # probability of |1> in the detector state




#==========================================================#
# 
# Main
#==========================================================#

if __name__ == "__main__":

    # Select the QasmSimulator from the Aer provider
    #simulator = AerSimulator()


    # Set up noise model
    coupling_map = simulator.configuration().coupling_map
    noise_model = NoiseModel.from_backend(simulator)
    print(noise_model)




    # Define operators
    H_op = SparsePauliOp("Z")
    P_op = SparsePauliOp("Z")
    HP_op = H_op ^ P_op

    print("Operator H * P:")
    print(HP_op)

    # Define quantum registers
    n_qubits_sys, n_qubits_det, n_qubits_env = 1, 1, 2

    n_bits_c = 1
    
    sys   = QuantumRegister(n_qubits_sys, 'sys')
    det   = QuantumRegister(n_qubits_det, 'det')
    env   = QuantumRegister(n_qubits_env, 'env')
    c_reg = ClassicalRegister(n_bits_c, "c")

    qc = QuantumCircuit(sys, det, env, c_reg)

    # Parameters
    Lambda = 1.0
    theta, phi = np.pi / 3, np.pi / 5
    p_deco = 0.2
    
    shots = 5000

    # Build and display the circuit
    build_circuit(qc, sys, det, env, theta, phi, p_deco, flag='imag')

    print("Final circuit:")
    print(qc)

'''