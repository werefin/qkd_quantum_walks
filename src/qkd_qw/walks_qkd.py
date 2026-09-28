# Discrete-time quantum walk circuits (circle, hypercube) without a measurement
# Backend for qkd_qw.protocol.QKD_Protocol_QW, which composes further ops before measuring
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Operator

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
        self.q_circuit = self._build_circuit()

    def _build_circuit(self):
        self._initialize_circuit()
        self._apply_F()
        self.circuit.barrier()
        for _ in range(self.t):
            self.circuit = self._coined_walk_step(self.circuit, self.walker_r, self.coin_r)
        self.circuit.barrier()
        return self.circuit

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
        self.q_circuit = self._build_circuit()

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
        return self.circuit
