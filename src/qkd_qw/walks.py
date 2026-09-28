# Discrete-time quantum walk circuits (circle, hypercube) with a walker-register measurement
# sweep_min_c computes c(t) exactly via Aer instead of rebuilding+sampling a depth-t circuit at every t
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.quantum_info import Operator
from qiskit_aer import AerSimulator

def _sweep_min_c(registers, init_circuit, step_circuit, n_report_qubits, t_max, threshold, patience=5000):
    simulator = AerSimulator(max_parallel_experiments=0, max_memory_mb=None)
    report_qubits = list(range(n_report_qubits))
    seed_circuit = init_circuit.copy()
    seed_circuit.save_statevector(label='sv0')
    tqc = transpile(seed_circuit, backend=simulator, optimization_level=1)
    current_sv = simulator.run(tqc, shots=1).result().data(0)['sv0']
    min_c = 0.5
    optimal_t = 1
    steps_since_improvement = 0
    t = 0
    chunk_size = 64
    t_limit = t_max - 1
    while t < t_limit:
        n_steps = min(chunk_size, t_limit - t)
        chunk_circuit = QuantumCircuit(*registers)
        chunk_circuit.set_statevector(current_sv)
        for i in range(1, n_steps + 1):
            chunk_circuit.compose(step_circuit, inplace=True)
            chunk_circuit.save_probabilities_dict(qubits=report_qubits, label=f'p{i}')
        chunk_circuit.save_statevector(label='sv_end')
        tqc = transpile(chunk_circuit, backend=simulator, optimization_level=1)
        data = simulator.run(tqc, shots=1).result().data(0)
        converged = False
        for i in range(1, n_steps + 1):
            c = float(max(data[f'p{i}'].values()))
            if c < min_c:
                significant = (min_c - c) > threshold
                min_c = c
                optimal_t = t + i
                steps_since_improvement = 0 if significant else steps_since_improvement + 1
            else:
                steps_since_improvement += 1
            if steps_since_improvement >= patience:
                converged = True
                break
        if converged:
            break
        current_sv = data['sv_end']
        t += n_steps
        chunk_size = min(chunk_size * 2, t_limit)
    return min_c, optimal_t

class QW_Circle:
    def __init__(self, P, t, initial_position=0, F='I', phi=0, theta=np.pi/4):
        self.P = P
        self.t = t
        self.initial_position = initial_position
        self.F = F
        self.phi = phi
        self.theta = theta
        self.n_walker_qubits = int(np.ceil(np.log2(2 * self.P)))
        self.walker_r = QuantumRegister(self.n_walker_qubits, 'q')
        self.coin_r = QuantumRegister(1, 'c')
        self.classic_r = ClassicalRegister(self.n_walker_qubits, 'r')
        self.circuit = QuantumCircuit(self.walker_r, self.coin_r, self.classic_r)
        self._build_circuit()

    def _build_circuit(self):
        self._initialize_circuit()
        self._apply_F()
        self.circuit.barrier()
        for step in range(self.t):
            self.circuit = self._coined_walk_step(self.circuit, self.walker_r, self.coin_r)
        self.circuit.barrier()
        self.circuit.measure(self.walker_r, reversed(self.classic_r))

    def _initialize_circuit(self):
        for i in range(self.n_walker_qubits):
            if self.initial_position & (1 << i):
                self.circuit.x(self.walker_r[self.n_walker_qubits - i - 1])
        self.circuit.barrier()

    def _apply_F(self):
        if self.F == 'I':
            pass
        elif self.F == 'X':
            self.circuit.h(self.coin_r)
        elif self.F == 'Y':
            self.circuit.h(self.coin_r)
            self.circuit.s(self.coin_r)
        else:
            raise ValueError("Invalid operator type. Choose 'I', 'X', or 'Y'")

    def coin_rotation_operator(self, coin_r):
        q_circuit = QuantumCircuit(len(coin_r))
        for qubit in range(len(coin_r)):
            q_circuit.u(self.theta, self.phi, 0, qubit)
        coin_rotation_operator = Operator(q_circuit)
        return coin_rotation_operator

    def _coined_walk_step(self, q_circuit, walker_r, coin_r):
        for qubit in coin_r:
            q_circuit.u(self.theta, self.phi, 0, qubit)
        for i in reversed(range(len(walker_r))):
            controls = [walker_r[v] for v in range(len(walker_r) - 1, i, -1)]
            controls.append(coin_r)
            q_circuit.mcx(controls, walker_r[i])
            if i != 0:
                q_circuit.x(walker_r[i])
        q_circuit.x(coin_r)
        for i in range(len(walker_r)):
            if i != 0:
                q_circuit.x(walker_r[i])
            controls = [walker_r[v] for v in range(len(walker_r) - 1, i, -1)]
            controls.append(coin_r)
            q_circuit.mcx(controls, walker_r[i])
        q_circuit.x(coin_r)
        return q_circuit

    def _one_step_circuit(self):
        step_circuit = QuantumCircuit(self.walker_r, self.coin_r)
        self._coined_walk_step(step_circuit, self.walker_r, self.coin_r)
        return step_circuit

    def sweep_min_c(self, t_max=50000, threshold=1e-05):
        init_circuit = QuantumCircuit(self.walker_r, self.coin_r)
        for i in range(self.n_walker_qubits):
            if self.initial_position & (1 << i):
                init_circuit.x(self.walker_r[self.n_walker_qubits - i - 1])
        if self.F == 'X':
            init_circuit.h(self.coin_r)
        elif self.F == 'Y':
            init_circuit.h(self.coin_r)
            init_circuit.s(self.coin_r)
        step_circuit = self._one_step_circuit()
        return _sweep_min_c((self.walker_r, self.coin_r), init_circuit, step_circuit,
                             self.n_walker_qubits, t_max, threshold)

    def draw_circuit(self):
        return self.circuit.draw("mpl")

    def plot_states_hist(self, shots=50000, title=None):
        import matplotlib.pyplot as plt
        from qiskit.visualization import plot_histogram
        simulator = AerSimulator(max_parallel_experiments=0, max_memory_mb=None)
        self.circuit = transpile(self.circuit, backend=simulator, optimization_level=1)
        job = simulator.run(self.circuit, shots=shots)
        results = job.result()
        counts = results.get_counts()
        fig, ax = plt.subplots(figsize=(12, 6))
        plot_histogram(counts, title=title or f'QW results (P={self.P})', sort='value_desc', ax=ax)
        ax.set_xlabel('Measured states')
        ax.set_ylabel('Counts')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def execute(self):
        simulator = AerSimulator(max_parallel_experiments=0, max_memory_mb=None)
        self.circuit = transpile(self.circuit, backend=simulator, optimization_level=1)
        results = simulator.run(self.circuit, shots=1).result()
        answer = results.get_counts()
        state = list(answer.keys())[0]
        return state

    def get_probabilities(self, shots=50000):
        simulator = AerSimulator(max_parallel_experiments=0, max_memory_mb=None)
        self.circuit = transpile(self.circuit, backend=simulator, optimization_level=1)
        results = simulator.run(self.circuit, shots=shots).result()
        counts = results.get_counts()
        probabilities = {}
        total = sum(counts.values())
        for state, count in counts.items():
            probabilities[state] = count / total
        return probabilities

class QW_Hypercube:
    def __init__(self, P, t, initial_position=0, F='I', coin_type='generic_rotation',
                 phi=0, theta=np.pi/4):
        self.P = P
        self.t = t
        self.initial_position = initial_position
        self.coin_type = coin_type
        self.phi = phi
        self.theta = theta
        self.F = F
        self.n_qubits = int(np.ceil(np.log2(2 ** P)))
        self.walker_r, self.coin_r, self.classic_r, self.circuit = self.hypercube_walk_circuit(self.n_qubits)
        self._initialize_states()
        self._build_circuit()

    def _initialize_states(self):
        for i in range(self.n_qubits):
            if self.initial_position & (1 << i):
                self.circuit.x(self.walker_r[self.n_qubits - i - 1])
        self.circuit.barrier()

    def hypercube_walk_circuit(self, n_qubits):
        walker_r = QuantumRegister(n_qubits, name='q')
        coin_r = QuantumRegister(n_qubits, name='c')
        classic_r = ClassicalRegister(n_qubits, name='r')
        q_circuit = QuantumCircuit(walker_r, coin_r, classic_r)
        return walker_r, coin_r, classic_r, q_circuit

    def coin_rotation_operator(self, coin_r):
        q_circuit = QuantumCircuit(len(coin_r))
        for qubit in range(len(coin_r)):
            q_circuit.u(self.theta, self.phi, 0, qubit)
        coin_rotation_operator = Operator(q_circuit)
        return coin_rotation_operator

    def grover_coin(self, coin_r):
        matrix_size = 2 ** len(coin_r)
        grover_matrix = np.full((matrix_size, matrix_size), 2 / matrix_size) - np.eye(matrix_size)
        return Operator(grover_matrix)

    def shift_operator(self, walker_r, coin_r):
        q_circuit = QuantumCircuit(walker_r, coin_r)
        for i in reversed(range(len(walker_r))):
            q_circuit.mcx(coin_r, walker_r[i])
            q_circuit.x(coin_r[-1])
            for j in range(1, len(coin_r)):
                if i & ((1 << j) - 1) == 0:
                    q_circuit.x(coin_r[-(j + 1)])
        return q_circuit

    def hypercube_walk_step(self, walker_r, coin_r):
        shift = self.shift_operator(walker_r, coin_r)
        walk_step = QuantumCircuit(walker_r, coin_r)
        if self.coin_type == 'generic_rotation':
            for qubit in coin_r:
                walk_step.u(self.theta, self.phi, 0, qubit)
        elif self.coin_type == 'grover':
            coin_operator = self.grover_coin(coin_r)
            walk_step.unitary(coin_operator, coin_r, label="G")
        walk_step.compose(shift, inplace=True)
        return walk_step

    def apply_F(self, q_circuit, coin_r):
        for qubit in coin_r:
            if self.F == "X":
                q_circuit.h(qubit)
            elif self.F == "Y":
                q_circuit.h(qubit)
                q_circuit.s(qubit)

    def _build_circuit(self):
        if self.coin_type == 'generic_rotation':
            self.apply_F(self.circuit, self.coin_r)
            self.circuit.barrier()
        for _ in range(self.t):
            walk_step = self.hypercube_walk_step(self.walker_r, self.coin_r)
            self.circuit.compose(walk_step, inplace=True)
        self.circuit.barrier()
        self.circuit.measure(self.walker_r, reversed(self.classic_r))

    def sweep_min_c(self, t_max=50000, threshold=1e-05):
        init_circuit = QuantumCircuit(self.walker_r, self.coin_r)
        for i in range(self.n_qubits):
            if self.initial_position & (1 << i):
                init_circuit.x(self.walker_r[self.n_qubits - i - 1])
        if self.coin_type == 'generic_rotation':
            self.apply_F(init_circuit, self.coin_r)
        step_circuit = self.hypercube_walk_step(self.walker_r, self.coin_r)
        return _sweep_min_c((self.walker_r, self.coin_r), init_circuit, step_circuit,
                             self.n_qubits, t_max, threshold)

    def draw_circuit(self):
        return self.circuit.draw("mpl")

    def plot_states_hist(self, shots=50000, title=None):
        import matplotlib.pyplot as plt
        from qiskit.visualization import plot_histogram
        simulator = AerSimulator(max_parallel_experiments=0, max_memory_mb=None)
        self.circuit = transpile(self.circuit, backend=simulator, optimization_level=1)
        results = simulator.run(self.circuit, shots=shots).result()
        counts = results.get_counts()
        fig, ax = plt.subplots(figsize=(12, 6))
        plot_histogram(counts, title=title or f'QW results (P={self.P})', sort='value_desc', ax=ax)
        ax.set_xlabel('Measured states')
        ax.set_ylabel('Counts')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def execute(self):
        simulator = AerSimulator(max_parallel_experiments=0, max_memory_mb=None)
        self.circuit = transpile(self.circuit, backend=simulator, optimization_level=1)
        results = simulator.run(self.circuit, shots=1).result()
        counts = results.get_counts()
        return list(counts.keys())[0]

    def get_probabilities(self, shots=50000):
        simulator = AerSimulator(max_parallel_experiments=0, max_memory_mb=None)
        self.circuit = transpile(self.circuit, backend=simulator, optimization_level=1)
        results = simulator.run(self.circuit, shots=shots).result()
        counts = results.get_counts()
        total_counts = sum(counts.values())
        probabilities = {state: count / total_counts for state, count in counts.items()}
        return probabilities
