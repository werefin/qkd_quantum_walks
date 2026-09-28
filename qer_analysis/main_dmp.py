# QER sweep under amplitude/phase damping noise, circle vs hypercube (writes results/qer_analysis/)
import os
import json
import numpy as np
from noise_models import Noise_Models
from qkd_protocol import QKD_Protocol_QW

n_iterations = 100000
F = 'I'
coin_type = 'generic_rotation'
phi = 0
theta = np.pi / 4

noise_models = Noise_Models()
results = []

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
repo_dir = os.path.join(repo_root, "results", "c_analysis")

circle_json_path = os.path.join(repo_dir, "c_qw_circle_results.json")
hypercube_json_path = os.path.join(repo_dir, "c_qw_hypercube_results.json")

if not os.path.exists(circle_json_path):
    raise FileNotFoundError(f"Circle JSON file not found at {circle_json_path}")
if not os.path.exists(hypercube_json_path):
    raise FileNotFoundError(f"Hypercube JSON file not found at {hypercube_json_path}")

with open(circle_json_path, 'r') as circle_file:
    circle_parameters = json.load(circle_file)
with open(hypercube_json_path, 'r') as hypercube_file:
    hypercube_parameters = json.load(hypercube_file)

def find_max_parameters_for_damping(P=1, target_qer=0.12, tolerance=1e-3, max_iterations=100, min_delta=1e-4):
    low_amplitude, high_amplitude = 0.0, 0.2
    low_phase, high_phase = 0.0, 0.2
    best_error_rate_amplitude = None
    best_error_rate_phase = None
    best_qer_diff = float('inf')
    for _ in range(max_iterations):
        p_amplitude = (low_amplitude + high_amplitude) / 2
        p_phase = (low_phase + high_phase) / 2
        noise_model = noise_models.create_combined_damping_noise(p_amplitude=p_amplitude,
                                                                 p_phase=p_phase)
        protocol = QKD_Protocol_QW(n_iterations=n_iterations, P=P, t=1, F='I',
                                   coin_type=coin_type, phi=0, theta=0,
                                   qw_type='circle', noise_model=noise_model)
        result = protocol.run_protocol(noise_model=noise_model)
        qer_z = result['qer_z']
        qer_diff = abs(qer_z - target_qer)
        if qer_diff < best_qer_diff or (qer_diff == best_qer_diff and (p_amplitude + p_phase) > (best_p_amplitude + best_p_phase)):
            best_p_amplitude = p_amplitude
            best_p_phase = p_phase
            best_qer_diff = qer_diff
        if qer_z < target_qer:
            low_amplitude = p_amplitude
            low_phase = p_phase
        else:
            high_amplitude = p_amplitude
            high_phase = p_phase
        if max(high_amplitude - low_amplitude, high_phase - low_phase) < min_delta:
            break
    return best_p_amplitude, best_p_phase

print("Finding maximum parameters for damping QER < 0.12 with P = 1...")
max_p_amplitude, max_p_phase = find_max_parameters_for_damping(P=1)
print(f"Maximum parameter for amplitude damping QER < 0.12: {max_p_amplitude:.6f}")
print(f"Maximum parameter for phase damping QER < 0.12: {max_p_phase:.6f}")

print("Processing QKD protocol with QW circle parameters...")
for entry in circle_parameters:
    P = entry['P']
    if P > 13:
        print(f"Stopping simulation for QW circle: P={P} (P > 13)")
        break
    optimal_t = entry['optimal_t']
    print(f"Starting simulation for QW circle: P={P}, optimal_t={optimal_t}")
    noise_model = noise_models.create_combined_damping_noise(p_amplitude=max_p_amplitude,
                                                             p_phase=max_p_phase)
    protocol = QKD_Protocol_QW(n_iterations=n_iterations, P=P, t=optimal_t,
                               F=F, coin_type=coin_type, phi=phi, theta=theta,
                               qw_type='circle', noise_model=noise_model)
    result = protocol.run_protocol(noise_model=noise_model)
    print(f"Protocol results for P={P}, optimal_t={optimal_t}:")
    print(f"QER (Z-basis): {result['qer_z']:.6f}")
    print(f"QER (QW-basis): {result['qer_qw']:.6f}")
    results.append({'type': 'circle', 'P': P, 'F': F, 'coin_type': coin_type, 'phi': phi,
                    'theta': theta, 't': optimal_t, 'qer_z': result['qer_z'], 'qer_qw': result['qer_qw']})

print("Processing QKD protocol with QW hypercube parameters...")
for entry in hypercube_parameters:
    P = entry['P']
    if P > 13:
        print(f"Stopping simulation for QW hypercube: P={P} (P > 13)")
        break
    optimal_t = entry['optimal_t']
    print(f"Starting simulation for QW hypercube: P={P}, optimal_t={optimal_t}")
    noise_model = noise_models.create_combined_damping_noise(p_amplitude=max_p_amplitude,
                                                             p_phase=max_p_phase)
    protocol = QKD_Protocol_QW(n_iterations=n_iterations, P=P, t=optimal_t,
                               F=F, coin_type=coin_type, phi=phi, theta=theta,
                               qw_type='hypercube', noise_model=noise_model)
    result = protocol.run_protocol(noise_model=noise_model)
    print(f"Protocol results for P={P}, optimal_t={optimal_t}:")
    print(f"QER (Z-basis): {result['qer_z']:.6f}")
    print(f"QER (QW-basis): {result['qer_qw']:.6f}")
    results.append({'type': 'hypercube', 'P': P, 'F': F, 'coin_type': coin_type, 'phi': phi,
                    'theta': theta, 't': optimal_t, 'qer_z': result['qer_z'], 'qer_qw': result['qer_qw']})

output_dir = os.path.join(repo_root, "results", "qer_analysis")
os.makedirs(output_dir, exist_ok=True)
results_file = os.path.join(output_dir, 'one_way_qkd_simulation_results_dmp.json')
with open(results_file, 'w') as results_file_obj:
    json.dump(results, results_file_obj, indent=4)
