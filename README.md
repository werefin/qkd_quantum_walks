## One-way QKD using quantum walks: security and noise resistance analysis

This repository is the official open-source simulation framework for the paper:

> **Strengthening security and noise resistance in one-way quantum key distribution protocols through hypercube-based quantum walks**:
> David Polzoni, Tommaso Bianchi, Mauro Conti, *IEEE International Conference on Quantum Computing and Engineering (QCE), 2026*, preprint: arXiv:2602.23261 [cs.CR]: https://arxiv.org/abs/2602.23261

The paper is published at **IEEE QCE26**. Until the proceedings version is available, please refer to the arXiv preprint linked above.

### About the paper

Quantum Key Distribution (QKD) provides information-theoretic security, but classical protocols such as BB84, while simple, offer limited resistance to eavesdropping and degrade quickly under realistic noise. The paper studies a one-way QKD protocol whose security depends exclusively on the underlying discrete-time Quantum Walk (QW) topology, rather than on the details of the protocol itself.

Its main contributions are:

- **Novel one-way QKD protocol based on QWs over a hypercube topology**: under identical parameters, it provides significantly enhanced security and noise resistance compared to the circular topology (i.e., the state of the art), strengthening protection against eavesdropping.
- **Efficient and extensible simulation framework** for one-way QKD protocols based on QWs, supporting both circular and hypercube topologies. It is implemented with IBM's Qiskit and enables noise-aware analysis under realistic noise models.

Together, these results establish a foundation for the design of *topology-aware* QKD protocols that combine enhanced noise tolerance with topologically driven security.

### Repository structure

| Path | Contents |
| --- | --- |
| [c_analysis/](c_analysis/) | Quantum walk circuits for both topologies ([qw_circle_hypercube.py](c_analysis/qw_circle_hypercube.py)) and the computation of the overlap parameter $c$ and of $\log_2(1/c)$ for circle ([main_c_circle.py](c_analysis/main_c_circle.py)) and hypercube ([main_c_hypercube.py](c_analysis/main_c_hypercube.py)). Results are cached in `c_analysis/c_results/`. |
| [qer_analysis/](qer_analysis/) | QKD protocol itself ([qkd_protocol.py](qer_analysis/qkd_protocol.py)), the QW backends used by it ([qw_circle_hypercube_qkd.py](qer_analysis/qw_circle_hypercube_qkd.py)), Qiskit noise models ([noise_models.py](qer_analysis/noise_models.py)), and Quantum Error Rate (QER) sweeps under depolarizing noise ([main_dn.py](qer_analysis/main_dn.py)) and under combined amplitude/phase damping ([main_dmp.py](qer_analysis/main_dmp.py)). |
| [optimized_parameters/](optimized_parameters/) | Grid searches over the protocol parameters ($P$, $F$, $\phi$, $\theta$, $t$) that minimise $c$ ([main_opt_param_c.py](optimized_parameters/main_opt_param_c.py)) and the corresponding QER-optimal settings, stored in `optimized_parameters/optimal_results/`. |
| [plot_scripts/](plot_scripts/) | Scripts that reproduce the figures of the paper from the JSON result files. |
| [intro_quantum_walks_qkd.ipynb](intro_quantum_walks_qkd.ipynb) | Tutorial notebook: step-by-step construction of the QW circuits and of the one-way QKD protocol, with plots. |

### Noise models

Two Qiskit `NoiseModel` families are used in the analysis, both applied to all single-qubit gates:

- **Depolarizing noise**: parameterized by $\lambda$ (see `create_depolarizing_noise`);
- **Combined amplitude and phase damping**: parameterized by $p_\text{amp}$ and $p_\text{phase}$ (see `create_combined_damping_noise`).

QER scripts perform a binary search over the noise strength to find the maximum noise level at which the protocol still stays below the target QER threshold, which is how the two topologies are compared.

### Installation and usage

```bash
git clone <this-repository>
cd qkd_quantum_walks
pip install qiskit qiskit-aer numpy matplotlib notebook
```

#### Running the simulations

```bash
# Overlap parameter c for the hypercube topology
python c_analysis/main_c_hypercube.py

# QER under depolarizing noise
python qer_analysis/main_dn.py

# Reproduce a figure from cached results
python plot_scripts/plot_c_results_comparison.py
```

The tutorial notebook can be opened directly:

```bash
jupyter notebook intro_quantum_walks_qkd.ipynb
```

> **Note**: `main_*.py` scripts were written to read from and write to a companion results repository, and contain a `GITHUB_USERNAME`/`GITHUB_PAT` block at the top for that purpose. Set those variables to your own values, or edit `repo_dir` to point at the local `c_results/` and `optimal_results/` directories already included here.

All simulations are parameterized at the top of each script (number of iterations, $P$ values, $F$, $\phi$, $\theta$, number of shots), so different scenarios can be explored by editing those constants.

### Citation

If you use this framework, please cite the IEEE QCE26 paper:

```bibtex
@inproceedings{polzoni2026hypercubeqkd,
  title     = {Strengthening security and noise resistance in one-way quantum key
               distribution protocols through hypercube-based quantum walks},
  author    = {Polzoni, David and Bianchi, Tommaso and Conti, Mauro},
  booktitle = {IEEE International Conference on Quantum Computing and Engineering (QCE)},
  year      = {2026},
  publisher = {IEEE}
}
```

The preprint can be cited as:

```bibtex
@misc{polzoni2026hypercubeqkd_arxiv,
  title        = {Strengthening security and noise resistance in one-way quantum key
                  distribution protocols through hypercube-based quantum walks},
  author       = {Polzoni, David and Bianchi, Tommaso and Conti, Mauro},
  year         = {2026},
  eprint       = {2602.23261},
  archivePrefix= {arXiv},
  primaryClass = {cs.CR},
  url          = {https://arxiv.org/abs/2602.23261}
}
```

### License

The code in this repository is released under the **MIT License**, see [LICENSE](LICENSE). You are free to use, modify, distribute and build upon it, including commercially, with no restrictions beyond keeping the copyright notice.

This applies to the simulation framework only. The paper itself is separate: the arXiv preprint is distributed under CC BY-NC-ND 4.0, and the proceedings version is subject to IEEE copyright.
