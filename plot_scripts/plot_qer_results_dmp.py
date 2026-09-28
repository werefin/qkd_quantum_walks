# QER-under-amplitude/phase-damping-noise bar plots: circle, hypercube, and comparison
import matplotlib.pyplot as plt
import json
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_folder = os.path.join(repo_root, "results", "plots")
os.makedirs(output_folder, exist_ok=True)

json_path = os.path.join(repo_root, "results", "qer_analysis", 'one_way_qkd_simulation_results_dmp.json')

with open(json_path, 'r') as file:
    data = json.load(file)

circle_data = [entry for entry in data if entry['type'] == 'circle']
hypercube_data = [entry for entry in data if entry['type'] == 'hypercube']

circle_P = [entry['P'] for entry in circle_data]
circle_qer_z = [entry['qer_z'] for entry in circle_data]

hypercube_P = [entry['P'] for entry in hypercube_data]
hypercube_qer_z = [entry['qer_z'] for entry in hypercube_data]

plt.figure(figsize=(12, 8))
plt.bar(circle_P, circle_qer_z, color='black', alpha=0.7)
plt.title(r'Maximally tolerated QER vs circle state space $P$: $F = I$, $\phi = 0$, $\theta = \pi / 4$', fontsize=16)
plt.xlabel('Circle state space $P$', fontsize=16)
plt.ylabel('Amplitude-phase damping noise $Q$', fontsize=16)
plt.xticks(ticks=circle_P, labels=circle_P, fontsize=14)
plt.yticks(fontsize=14)
plt.grid(False)
plt.tight_layout()
circle_plot_path = os.path.join(output_folder, 'qer_z_circle_plot_dmp.png')
plt.savefig(circle_plot_path)
plt.show()

plt.figure(figsize=(12, 8))
plt.bar(hypercube_P, hypercube_qer_z, color='gray', alpha=0.7)
plt.title(r'Maximally tolerated QER vs hypercube state space $P$: $F = I$, $\phi = 0$, $\theta = \pi / 4$', fontsize=16)
plt.xlabel('Hypercube state space $P$', fontsize=16)
plt.ylabel('Amplitude-phase damping $Q$', fontsize=16)
plt.xticks(ticks=hypercube_P, labels=hypercube_P, fontsize=14)
plt.yticks(fontsize=14)
plt.grid(False)
plt.tight_layout()
hypercube_plot_path = os.path.join(output_folder, 'qer_z_hypercube_plot_dmp.png')
plt.savefig(hypercube_plot_path)
plt.show()

plt.figure(figsize=(12, 8))
bar_width = 0.4
x_circle = [p - bar_width / 2 for p in circle_P]
x_hypercube = [p + bar_width / 2 for p in hypercube_P]
plt.bar(x_circle, circle_qer_z, width=bar_width, color='black', alpha=0.7, label='circle')
plt.bar(x_hypercube, hypercube_qer_z, width=bar_width, color='gray', alpha=0.7, label='hypercube')
plt.title('Comparison of $Q$ circle vs hypercube: amplitude-phase damping noise', fontsize=16)
plt.xlabel('State space $P$', fontsize=16)
plt.ylabel('Amplitude-phase damping $Q$', fontsize=16)
plt.xticks(ticks=circle_P, labels=circle_P, fontsize=14)
plt.yticks(fontsize=14)
plt.legend(fontsize=14)
plt.grid(False)
plt.tight_layout()
comparison_plot_path = os.path.join(output_folder, 'qer_z_comparison_plot_dmp.png')
plt.savefig(comparison_plot_path)
plt.show()
