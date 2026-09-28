# Bar plot of security parameter c vs circle state space P (Fig. 2 of the paper)
import json
import matplotlib.pyplot as plt
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_folder = os.path.join(repo_root, "results", "plots")
os.makedirs(output_folder, exist_ok=True)

json_path = os.path.join(repo_root, "results", "c_analysis", 'c_qw_circle_results.json')

with open(json_path, 'r') as file:
    data = json.load(file)

P_vals = [entry['P'] for entry in data]
c_vals = [entry['c'] for entry in data]

desired_P_values = list(range(1, 14)) + [79, 129, 179, 229]

filtered_data = [(P, c) for P, c in zip(P_vals, c_vals) if P in desired_P_values]
filtered_P, filtered_c = zip(*filtered_data)

custom_positions = list(range(len(filtered_P)))

plt.figure(figsize=(12, 8))

bars = plt.bar(custom_positions, filtered_c, width=0.6, color='black', alpha=0.7)

for i in range(1, len(filtered_P)):
    if filtered_P[i] > 13 and filtered_P[i] - filtered_P[i - 1] > 1:
        plt.text((custom_positions[i] + custom_positions[i - 1]) / 2, min(filtered_c) - 0.01,
            	 "...", ha='center', va='center', fontsize=14, color='black')

plt.xticks(ticks=custom_positions, labels=filtered_P, fontsize=14)
plt.yticks(fontsize=14)

plt.title(r'Security parameter $c$ vs circle state space $P$: $F = I$, $\phi = 0$, $\theta = \pi / 4$', fontsize=16)
plt.xlabel('Circle state space $P$', fontsize=16)
plt.ylabel('Security parameter $c$', fontsize=16)
plt.grid(False)

plt.tight_layout()

plot_path = os.path.join(output_folder, 'c_qw_circle_plot_all.png')
plt.savefig(plot_path)
plt.show()
