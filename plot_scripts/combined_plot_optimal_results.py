# QER vs P, optimal vs non-optimal, side-by-side depolarizing/damping noise (Fig. 5 of the paper)
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

non_optimal_data_dmp = load_json("one_way_qkd_simulation_results_dmp.json", "qer_analysis")
optimal_data_circle_dmp = load_json("optimal_results_qer_dmp_circle.json", "optimized_parameters")
optimal_data_hypercube_dmp = load_json("optimal_results_qer_dmp_hypercube.json", "optimized_parameters")

non_optimal_data_dn = load_json("one_way_qkd_simulation_results_dn.json", "qer_analysis")
optimal_data_circle_dn = load_json("optimal_results_qer_dn_circle.json", "optimized_parameters")
optimal_data_hypercube_dn = load_json("optimal_results_qer_dn_hypercube.json", "optimized_parameters")

def extract_qer_z_vs_P(data, q_type):
    P_values = []
    qer_z_values = []
    for entry in data:
        if entry["type"] == q_type:
            P_values.append(entry["P"])
            qer_z_values.append(entry["qer_z"])
    return np.array(P_values), np.array(qer_z_values)

P_circle_dmp, qer_z_circle_dmp = extract_qer_z_vs_P(non_optimal_data_dmp, "circle")
P_hypercube_dmp, qer_z_hypercube_dmp = extract_qer_z_vs_P(non_optimal_data_dmp, "hypercube")
P_opt_circle_dmp, qer_z_opt_circle_dmp = extract_qer_z_vs_P(optimal_data_circle_dmp, "circle")
P_opt_hypercube_dmp, qer_z_opt_hypercube_dmp = extract_qer_z_vs_P(optimal_data_hypercube_dmp, "hypercube")

P_circle_dn, qer_z_circle_dn = extract_qer_z_vs_P(non_optimal_data_dn, "circle")
P_hypercube_dn, qer_z_hypercube_dn = extract_qer_z_vs_P(non_optimal_data_dn, "hypercube")
P_opt_circle_dn, qer_z_opt_circle_dn = extract_qer_z_vs_P(optimal_data_circle_dn, "circle")
P_opt_hypercube_dn, qer_z_opt_hypercube_dn = extract_qer_z_vs_P(optimal_data_hypercube_dn, "hypercube")

fig, axs = plt.subplots(1, 2, figsize=(20, 8))

circle_color = 'orangered'
hypercube_color = 'royalblue'

P_values_combined = np.unique(np.concatenate([P_circle_dmp, P_hypercube_dmp, P_circle_dn, P_hypercube_dn]))

axs[0].plot(P_circle_dn, qer_z_circle_dn, color=circle_color, marker='o', markersize=8, linewidth=2, label="non-optimal (circle)", markeredgewidth=2)
axs[0].plot(P_opt_circle_dn, qer_z_opt_circle_dn, color=circle_color, marker='D', markersize=8, linewidth=2, label="optimal (circle)", linestyle='--', markeredgewidth=2)
axs[0].plot(P_hypercube_dn, qer_z_hypercube_dn, color=hypercube_color, marker='s', markersize=8, linewidth=2, label="non-optimal (hypercube)", markeredgewidth=2)
axs[0].plot(P_opt_hypercube_dn, qer_z_opt_hypercube_dn, color=hypercube_color, marker='^', markersize=8, linewidth=2, label="optimal (hypercube)", linestyle='--', markeredgewidth=2)

axs[0].set_xlabel("State space $P$", fontsize=16)
axs[0].set_ylabel("Maximally tolerated QER $Q$", fontsize=16)
axs[0].set_title("Depolarizing noise", fontsize=16)
axs[0].legend(fontsize=14, loc="upper left", frameon=True, edgecolor="black")
axs[0].grid(True, linestyle='--', alpha=0.5)
axs[0].tick_params(axis='both', which='major', labelsize=14)
axs[0].set_xticks(P_values_combined)

axs[1].plot(P_circle_dmp, qer_z_circle_dmp, color=circle_color, marker='o', markersize=8, linewidth=2, label="non-optimal (circle)", markeredgewidth=2)
axs[1].plot(P_opt_circle_dmp, qer_z_opt_circle_dmp, color=circle_color, marker='D', markersize=8, linewidth=2, label="optimal (circle)", linestyle='--', markeredgewidth=2)
axs[1].plot(P_hypercube_dmp, qer_z_hypercube_dmp, color=hypercube_color, marker='s', markersize=8, linewidth=2, label="non-optimal (hypercube)", markeredgewidth=2)
axs[1].plot(P_opt_hypercube_dmp, qer_z_opt_hypercube_dmp, color=hypercube_color, marker='^', markersize=8, linewidth=2, label="optimal (hypercube)", linestyle='--', markeredgewidth=2)

axs[1].set_xlabel("State space $P$", fontsize=16)
axs[1].set_ylabel("Maximally tolerated QER $Q$", fontsize=16)
axs[1].set_title("Amplitude-phase damping noise", fontsize=16)
axs[1].legend(fontsize=14, loc="upper left", frameon=True, edgecolor="black")
axs[1].grid(True, linestyle='--', alpha=0.5)
axs[1].tick_params(axis='both', which='major', labelsize=14)
axs[1].set_xticks(P_values_combined)

plt.tight_layout()

plt.savefig(os.path.join(output_folder, "combined_optimal_results_dn_dmp.png"))

plt.show()
