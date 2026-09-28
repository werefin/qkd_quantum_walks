import numpy as np
import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from c_analysis import QW_Circle, QW_Hypercube

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
repo_dir = os.path.join(repo_root, "results", "optimized_parameters")
os.makedirs(repo_dir, exist_ok=True)

P_values = list(range(1, 14, 2))
F_values = ['I', 'X', 'Y']
phi_values = [k * np.pi / 10 for k in range(11)]
theta_values = [k * np.pi / 10 for k in range(11)]

best_results = {"circle": [], "hypercube": []}

print("Finding optimal c values...")
for P in P_values:
    print(f"Processing P = {P}...")
    best_c_circle = float('inf')
    best_combination_c_circle = None
    best_c_hypercube = float('inf')
    best_combination_c_hypercube = None
    for topology in ['circle', 'hypercube']:
        for F in F_values:
            for phi in phi_values:
                for theta in theta_values:
                    print(f"Testing: {topology}, P={P}, F={F}, phi={phi:.2f}, theta={theta:.2f}")
                    significant_threshold = 1e-5
                    if topology == 'circle':
                        qw = QW_Circle(P=P, t=0, initial_position=P, F=F, phi=phi, theta=theta)
                    else:
                        qw = QW_Hypercube(P=P, t=0, initial_position=2**(P - 1), F=F, coin_type='generic_rotation', phi=phi, theta=theta)
                    min_c, optimal_t = qw.sweep_min_c(t_max=50000, threshold=significant_threshold)
                    log_inv_c = -np.log2(min_c)
                    if topology == 'circle':
                        if min_c < best_c_circle:
                            best_c_circle = min_c
                            best_combination_c_circle = {"type": topology, "P": P, "F": F, "phi": phi, "theta": theta, "optimal_t": optimal_t, "c": min_c, "log_inv_c": log_inv_c}
                    else:
                        if min_c < best_c_hypercube:
                            best_c_hypercube = min_c
                            best_combination_c_hypercube = {"type": topology, "P": P, "F": F, "phi": phi, "theta": theta, "optimal_t": optimal_t, "c": min_c, "log_inv_c": log_inv_c}
    if best_combination_c_circle:
        best_results["circle"].append(best_combination_c_circle)
    if best_combination_c_hypercube:
        best_results["hypercube"].append(best_combination_c_hypercube)
    print(f"Optimal combination for circle (P={P}): {best_combination_c_circle}")
    print(f"Optimal combination for hypercube (P={P}): {best_combination_c_hypercube}")

optimal_results_path = os.path.join(repo_dir, 'optimized_parameters_c.json')
with open(optimal_results_path, 'w') as f:
    json.dump(best_results, f, indent=4)