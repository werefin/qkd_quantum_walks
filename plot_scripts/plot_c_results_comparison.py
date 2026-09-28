# Bar plot comparing security parameter c: circle vs hypercube (Fig. 3 of the paper)
import json
import matplotlib.pyplot as plt
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_folder = os.path.join(repo_root, "results", "plots")
os.makedirs(output_folder, exist_ok=True)

c_results_dir = os.path.join(repo_root, "results", "c_analysis")
circle_json_path = os.path.join(c_results_dir, 'c_qw_circle_results.json')
hypercube_json_path = os.path.join(c_results_dir, 'c_qw_hypercube_results.json')

with open(circle_json_path, 'r') as file:
    circle_data = json.load(file)
circle_filtered_data = [entry for entry in circle_data if entry['P'] <= 13]
circle_P_vals = [entry['P'] for entry in circle_filtered_data]
circle_c_vals = [entry['c'] for entry in circle_filtered_data]

with open(hypercube_json_path, 'r') as file:
    hypercube_data = json.load(file)
hypercube_P_vals = [entry['P'] for entry in hypercube_data]
hypercube_c_vals = [entry['c'] for entry in hypercube_data]

plt.figure(figsize=(12, 8))

all_P_vals = sorted(set(circle_P_vals + hypercube_P_vals))

P_to_idx = {P: idx for idx, P in enumerate(all_P_vals)}

x_positions_circle = [P_to_idx[P] for P in circle_P_vals]
x_positions_hypercube = [P_to_idx[P] + 0.4 for P in hypercube_P_vals]

plt.bar(x_positions_circle, circle_c_vals, width=0.4,
    	color='black', alpha=0.7, label='circle', align='center')

plt.bar(x_positions_hypercube, hypercube_c_vals, width=0.4,
	color='gray', alpha=0.7, label='hypercube', align='center')

plt.title('Security parameter $c$ comparison: QW circle vs QW hypercube', fontsize=16)
plt.xlabel('State space $P$', fontsize=16)
plt.ylabel('Security parameter $c$', fontsize=16)
plt.grid(False)
plt.legend()

plt.xticks(ticks=[x + 0.2 for x in range(len(all_P_vals))], labels=all_P_vals, fontsize=14)
plt.yticks(fontsize=14)
plt.legend(fontsize=14)

plt.tight_layout()

comparison_plot_path = os.path.join(output_folder, 'c_qw_comparison_plot.png')
plt.savefig(comparison_plot_path)
plt.show()
