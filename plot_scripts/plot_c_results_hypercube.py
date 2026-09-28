# Bar plot of security parameter c vs hypercube state space P
import json
import matplotlib.pyplot as plt
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_folder = os.path.join(repo_root, "results", "plots")
os.makedirs(output_folder, exist_ok=True)

json_path = os.path.join(repo_root, "results", "c_analysis", 'c_qw_hypercube_results.json')

with open(json_path, 'r') as file:
    data = json.load(file)

P_vals = [entry['P'] for entry in data]
c_vals = [entry['c'] for entry in data]

plt.figure(figsize=(12, 8))

bars = plt.bar(range(len(P_vals)), c_vals, width=0.6, color='gray', alpha=0.7)

plt.title(r'Security parameter $c$ vs hypercube state space $P$: $F = I$, $\phi = 0$, $\theta = \pi / 4$', fontsize=18)
plt.xlabel('Hypercube state space $P$', fontsize=16)
plt.ylabel('Security parameter $c$', fontsize=16)

plt.xticks(ticks=range(len(P_vals)), labels=P_vals, fontsize=14)
plt.grid(False)
plt.yticks(fontsize=14)

plt.tight_layout()

plot_path = os.path.join(output_folder, 'c_qw_hypercube_plot.png')
plt.savefig(plot_path)
plt.show()
