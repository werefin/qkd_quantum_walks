import numpy as np
import json
import os
from qw_circle_hypercube import QW_Hypercube

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
repo_dir = os.path.join(repo_root, "results", "c_analysis")
os.makedirs(repo_dir, exist_ok=True)

P_values = list(range(1, 14, 2))
results = []

phi = 0
theta = np.pi / 4
t_max = 50000
significant_threshold = 1e-05

print("P\tmin_c\tlog_2(1/c)\tt")
print("-" * 38)

for P in P_values:
    initial_position = 2 ** (P - 1)
    qw = QW_Hypercube(P=P, t=0, initial_position=initial_position, F='I',
                      coin_type='generic_rotation', phi=phi, theta=theta)
    min_c, optimal_t = qw.sweep_min_c(t_max=t_max, threshold=significant_threshold)

    log_inv_c = -np.log2(min_c)
    results.append((P, min_c, log_inv_c, optimal_t))
    print(f"{P}\t{min_c:.4f}\t{log_inv_c:.4f}\t{optimal_t}")

results_json = [{"P": P, "c": c, "log_2(1/c)": log_c, "optimal_t": t} for P, c, log_c, t in results]
json_path = os.path.join(repo_dir, 'c_qw_hypercube_results.json')
with open(json_path, 'w') as f:
    json.dump(results_json, f, indent=4)
