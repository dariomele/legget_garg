import numpy as np
import os
import csv
from qiskit.circuit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from dotenv import load_dotenv



#==========================================================#
# 
# Run card printing
#==========================================================#

def print_runcard(output_folder, **kwargs):
    runcard_path = os.path.join(output_folder, "runcard.txt")
    with open(runcard_path, "w") as runcard:
        for key, value in kwargs.items():
            runcard.write(f"{key}: {value}\n")