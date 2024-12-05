import numpy as np
import os
import csv
from qiskit.circuit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from dotenv import load_dotenv

load_dotenv() # load the .env file in which is contained the IBM token

#==========================================================#
# 
# loading the backend on which to perform simulations
#==========================================================#

def load_backend(simulate, noise, min_num_qubits):
    if simulate:
        if noise:
            from qiskit_ibm_runtime.fake_provider import FakeBogotaV2
            noise_model = NoiseModel.from_backend(FakeBogotaV2())
            return AerSimulator(noise_model=noise_model)
        else:
            return AerSimulator()
    else:
        from qiskit_ibm_runtime import QiskitRuntimeService
        try:
            service = QiskitRuntimeService()
        except Exception:
            QiskitRuntimeService.save_account(
                channel="ibm_quantum", token=os.getenv("IBM_QUANTUM_API_TOKEN"), set_as_default=True
            )
        return service.least_busy(operational=True, simulator=False, min_num_qubits=min_num_qubits)
