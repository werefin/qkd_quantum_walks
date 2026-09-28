# One-way QKD protocol over circle/hypercube quantum walks
# run_protocol batches iterations by circuit signature instead of one job per iteration
import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator
from .walks_qkd import QW_Circle, QW_Hypercube

class QKD_Protocol_QW:
    _circuit_cache = {}

    def __init__(self, n_iterations, P, t, F='I', coin_type='generic_rotation', phi=0, theta=np.pi/4, qw_type='circle', noise_model=None):
        self.n_iterations = n_iterations
        self.P = P
        self.t = t
        self.F = F
        self.coin_type = coin_type
        self.phi = phi
        self.theta = theta
        self.qw_type = qw_type
        self.noise_model = noise_model
        if self.qw_type == 'circle':
            self.state_space_size = 2 * P
        elif self.qw_type == 'hypercube':
            self.state_space_size = 2 ** P
        else:
            raise ValueError("Invalid QW type. Choose 'circle' or 'hypercube'")
        self.n_qubits = int(np.ceil(np.log2(self.state_space_size)))

    def prepare_alice_state(self, w_a, i_a):
        if self.qw_type == 'circle':
            if w_a == 0:
                q_circuit = QW_Circle(P=self.P, t=0, initial_position=i_a,
                                      F=self.F, phi=self.phi, theta=self.theta)
            elif w_a == 1:
                q_circuit = QW_Circle(P=self.P, t=self.t, initial_position=i_a,
                                      F=self.F, phi=self.phi, theta=self.theta)
        elif self.qw_type == 'hypercube':
            if w_a == 0:
                q_circuit = QW_Hypercube(P=self.P, t=0, initial_position=i_a,
                                         F=self.F, coin_type=self.coin_type,
                                         phi=self.phi, theta=self.theta)
            elif w_a == 1:
                q_circuit = QW_Hypercube(P=self.P, t=self.t, initial_position=i_a,
                                         F=self.F, coin_type=self.coin_type,
                                         phi=self.phi, theta=self.theta)
        else:
            raise ValueError("Unsupported QW type. Supported types are 'circle' and 'hypercube'")
        return q_circuit

    def bob_measurement(self, q_circuit_obj, w_b):
        q_circuit = q_circuit_obj.circuit
        if w_b == 0:
            q_circuit.measure(q_circuit_obj.walker_r, reversed(q_circuit_obj.classic_r))
        elif w_b == 1:
            if self.qw_type == 'circle':
                qc_to_invert = QW_Circle(P=self.P, t=self.t, initial_position=0,
                                         F=self.F, phi=self.phi, theta=self.theta)
            elif self.qw_type == 'hypercube':
                qc_to_invert = QW_Hypercube(P=self.P, t=self.t, initial_position=0,
                                            F=self.F, coin_type=self.coin_type,
                                            phi=self.phi, theta=self.theta)
            else:
                raise ValueError("Unsupported QW type. Supported types are 'circle' and 'hypercube'")
            q_circuit.compose(qc_to_invert.circuit.inverse(), inplace=True)
            q_circuit.measure(q_circuit_obj.walker_r, reversed(q_circuit_obj.classic_r))
        return q_circuit

    def calculate_error_rate(self, alice_bits, bob_bits):
        if not alice_bits:
            return 0.0
        errors = sum(a != b for a, b in zip(alice_bits, bob_bits))
        return errors / len(alice_bits)

    @staticmethod
    def _noise_signature(noise_model):
        if noise_model is None:
            return None
        return tuple(sorted(noise_model.basis_gates))

    def _cache_key(self, w_a, i_a, w_b, noise_sig):
        return (self.qw_type, self.P, self.t, self.F, self.coin_type,
                self.phi, self.theta, w_a, i_a, w_b, noise_sig)

    def _get_transpiled_circuit(self, w_a, i_a, w_b, simulator, noise_sig):
        key = self._cache_key(w_a, i_a, w_b, noise_sig)
        cached = QKD_Protocol_QW._circuit_cache.get(key)
        if cached is not None:
            return cached
        q_circuit_obj = self.prepare_alice_state(w_a, i_a)
        q_circuit = self.bob_measurement(q_circuit_obj, w_b)
        transpiled = transpile(q_circuit, backend=simulator, optimization_level=1)
        QKD_Protocol_QW._circuit_cache[key] = transpiled
        return transpiled

    def run_protocol(self, noise_model):
        w_a_arr = np.random.randint(2, size=self.n_iterations)
        i_a_arr = np.random.randint(self.state_space_size, size=self.n_iterations)
        w_b_arr = np.random.randint(2, size=self.n_iterations)
        combos = np.stack([w_a_arr, i_a_arr, w_b_arr], axis=1)
        unique_combos, group_counts = np.unique(combos, axis=0, return_counts=True)
        simulator = AerSimulator(max_parallel_experiments=0, max_memory_mb=None, noise_model=noise_model)
        noise_sig = self._noise_signature(noise_model)
        alice_bits = []
        bob_bits = []
        basis_choices = []
        for (w_a, i_a, w_b), shots in zip(unique_combos, group_counts):
            w_a, i_a, w_b, shots = int(w_a), int(i_a), int(w_b), int(shots)
            if w_a != w_b:
                continue
            circuit = self._get_transpiled_circuit(w_a, i_a, w_b, simulator, noise_sig)
            counts = simulator.run(circuit, shots=shots).result().get_counts()
            for bitstring, count in counts.items():
                j_b = int(bitstring, 2)
                if j_b < self.state_space_size:
                    alice_bits.extend([i_a] * count)
                    bob_bits.extend([j_b] * count)
                    basis_choices.extend([w_a] * count)
        alice_z_bits = [alice_bits[i] for i in range(len(basis_choices)) if basis_choices[i] == 0]
        bob_z_bits = [bob_bits[i] for i in range(len(basis_choices)) if basis_choices[i] == 0]
        q_z = self.calculate_error_rate(alice_z_bits, bob_z_bits)
        alice_qw_bits = [alice_bits[i] for i in range(len(basis_choices)) if basis_choices[i] == 1]
        bob_qw_bits = [bob_bits[i] for i in range(len(basis_choices)) if basis_choices[i] == 1]
        q_w = self.calculate_error_rate(alice_qw_bits, bob_qw_bits)
        return {'raw_key_alice': alice_bits, 'raw_key_bob': bob_bits,
                'basis_choices': basis_choices, 'qer_z': q_z, 'qer_qw': q_w}
