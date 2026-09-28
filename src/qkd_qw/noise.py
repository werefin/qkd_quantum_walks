# Qiskit noise models used by the QKD protocol simulations
import numpy as np
from qiskit_aer.noise import (depolarizing_error, amplitude_damping_error, phase_damping_error)
from qiskit_aer.noise import NoiseModel

class Noise_Models:
    def __init__(self):
        pass

    def create_depolarizing_noise(self, d_lambda):
        noise_model = NoiseModel()
        error_1q = depolarizing_error(d_lambda, 1)
        single_qubit_gates = ['u', 'u1', 'u2', 'u3', 'x', 'y', 'z']
        for gate in single_qubit_gates:
            noise_model.add_all_qubit_quantum_error(error_1q, gate)
        return noise_model

    def create_combined_damping_noise(self, p_amplitude, p_phase):
        noise_model = NoiseModel()
        amplitude_damping = amplitude_damping_error(p_amplitude)
        phase_damping = phase_damping_error(p_phase)
        combined_error = amplitude_damping.compose(phase_damping)
        noise_model.add_all_qubit_quantum_error(combined_error, ['u', 'u1', 'u2', 'u3', 'x', 'y', 'z'])
        return noise_model
