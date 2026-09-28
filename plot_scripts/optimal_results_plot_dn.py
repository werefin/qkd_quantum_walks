# QER vs P, optimal vs non-optimal parameters, depolarizing noise (Fig. 5a of the paper)
import json
import matplotlib.pyplot as plt
import numpy as np
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_folder = os.path.join(repo_root, "results", "plots")
os.makedirs(output_folder, exist_ok=True)

def load_json(filename, subdir):
    with open(os.path.join(repo_root, "results", subdir, filename), 'r') as file:
        return json.load(file)

non_optimal_data = load_json("one_way_qkd_simulation_results_dn.json", "qer_analysis")
optimal_data_circle = load_json("optimal_results_qer_dn_circle.json", "optimized_parameters")
optimal_data_hypercube = load_json("optimal_results_qer_dn_hypercube.json", "optimized_parameters")

def extract_qer_z_vs_P(data, q_type):
    P_values = []
    qer_z_values = []
    for entry in data:
        if entry["type"] == q_type:
            P_values.append(entry["P"])
            qer_z_values.append(entry["qer_z"])
    return np.array(P_values), np.array(qer_z_values)

P_circle, qer_z_circle = extract_qer_z_vs_P(non_optimal_data, "circle")
P_hypercube, qer_z_hypercube = extract_qer_z_vs_P(non_optimal_data, "hypercube")

P_opt_circle, qer_z_opt_circle = extract_qer_z_vs_P(optimal_data_circle, "circle")
P_opt_hypercube, qer_z_opt_hypercube = extract_qer_z_vs_P(optimal_data_hypercube, "hypercube")

plt.figure(figsize=(12, 8))

circle_color = 'orangered'
hypercube_color = 'royalblue'

plt.plot(P_circle, qer_z_circle, color=circle_color, marker='o', markersize=8, linewidth=2, label="non-optimal (circle)", markerfacecolor='white', markeredgewidth=2)
plt.plot(P_opt_circle, qer_z_opt_circle, color=circle_color, marker='D', markersize=8, linewidth=2, label="optimal (circle)", linestyle='--', markerfacecolor='white', markeredgewidth=2)

plt.plot(P_hypercube, qer_z_hypercube, color=hypercube_color, marker='s', markersize=8, linewidth=2, label="non-optimal (hypercube)", markerfacecolor='white', markeredgewidth=2)
plt.plot(P_opt_hypercube, qer_z_opt_hypercube, color=hypercube_color, marker='^', markersize=8, linewidth=2, label="optimal (hypercube)", linestyle='--', markerfacecolor='white', markeredgewidth=2)

plt.xlabel("State space $P$", fontsize=16)
plt.ylabel("Maximally tolerated QER $Q$", fontsize=16)
plt.title("Comparison of $Q$ vs $P$ for optimal and non-optimal cases: depolarizing noise", fontsize=16)
plt.legend(fontsize=14, loc="upper left", frameon=True, edgecolor="black")

plt.grid(True, linestyle='--', alpha=0.5)
plt.xticks(np.unique(np.concatenate((P_circle, P_hypercube))), fontsize=14)
plt.yticks(fontsize=14)
plt.tight_layout()

plt.savefig(os.path.join(output_folder, "optimal_results_qer_z_vs_p_dn.png"))

plt.show()
