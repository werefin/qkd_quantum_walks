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
| [src/qkd_qw/](src/qkd_qw/) | Installable library: QW circuits ([walks.py](src/qkd_qw/walks.py), [walks_qkd.py](src/qkd_qw/walks_qkd.py)), the QKD protocol ([protocol.py](src/qkd_qw/protocol.py)) and noise models ([noise.py](src/qkd_qw/noise.py)). This is the canonical implementation; see [Performance](#performance) below. |
| [c_analysis/](c_analysis/) | Computation of the overlap parameter $c$ and of $\log_2(1/c)$ for circle ([main_c_circle.py](c_analysis/main_c_circle.py)) and hypercube ([main_c_hypercube.py](c_analysis/main_c_hypercube.py)). |
| [qer_analysis/](qer_analysis/) | Quantum Error Rate (QER) sweeps under depolarizing noise ([main_dn.py](qer_analysis/main_dn.py)) and under combined amplitude/phase damping ([main_dmp.py](qer_analysis/main_dmp.py)). |
| [optimized_parameters/](optimized_parameters/) | Grid searches over the protocol parameters ($P$, $F$, $\phi$, $\theta$, $t$) that minimise $c$ ([main_opt_param_c.py](optimized_parameters/main_opt_param_c.py)) and the corresponding QER-optimal settings ([main_opt_param_qer_dn.py](qer_analysis/main_opt_param_qer_dn.py), [main_opt_param_qer_dmp.py](qer_analysis/main_opt_param_qer_dmp.py)). |
| [plot_scripts/](plot_scripts/) | Scripts that reproduce the figures of the paper from the JSON result files. |
| [results/](results/) | All JSON/PNG outputs from the scripts above, organized by module: `c_analysis/`, `optimized_parameters/`, `qer_analysis/`, `plots/`. Official results for the IEEE QCE26 paper. |
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
pip install -e .            # installs the qkd_qw library (numpy, qiskit, qiskit-aer)
pip install -e ".[notebook]" # optional: matplotlib + jupyter, for plots and the tutorial
```

#### Running the simulations

```bash
# Overlap parameter c for the hypercube topology -> results/c_analysis/
python c_analysis/main_c_hypercube.py

# QER under depolarizing noise -> results/qer_analysis/
python qer_analysis/main_dn.py

# Reproduce a figure from results/ -> results/plots/
python plot_scripts/plot_c_results_comparison.py
```

The tutorial notebook can be opened directly:

```bash
jupyter notebook intro_quantum_walks_qkd.ipynb
```

All scripts read/write JSON and PNG outputs under [results/](results/) (relative to the repository root), and are parameterized at the top of each file (number of iterations, $P$ values, $F$, $\phi$, $\theta$), so different scenarios can be explored by editing those constants.

### Performance

The `qkd_qw` library is the canonical implementation behind every script in this repository (`c_analysis/`, `qer_analysis/` and `optimized_parameters/` import it through thin backward-compatible shims), and it is built for speed:

- **Exact, incremental overlap-parameter search** (`QW_Circle.sweep_min_c` / `QW_Hypercube.sweep_min_c`): security parameter $c(t) = \max_x |\alpha_{x,y}|^2$ (Eq. 18 of the paper) is computed exactly (no shot noise) through Aer, evolved step by step in exponentially growing chunks that resume from the previous chunk's saved statevector, instead of rebuilding a depth-$t$ circuit and estimating $c$ from `shots=100000` at every $t$ explored. Aer is used rather than `qiskit.quantum_info.Statevector` because the latter's default multi-controlled-X synthesis is exponential in the number of controls (measured: a single hypercube step at $P=5$ took 29ms but 40s at $P=9$); Aer applies `mcx` natively, closing that gap. The search stops once 5000 steps pass without a new minimum (a discrete-time quantum walk is unitary and never truly settles, so a plain plateau/tolerance check on its own is not reliable --> see the note below). This is available as a faster alternative for future `c` computations.
- **Batched, cached QKD protocol simulation** (`QKD_Protocol_QW.run_protocol`): a protocol run is grouped by its $(w_A, i_A, w_B)$ circuit signature, each distinct circuit is transpiled once against a noise-matched simulator (cached across noise levels sharing the same noise-model gate signature too), and simulated with `shots=<group size>` instead of one job per iteration. Measured: **100-1000x** fewer/cheaper simulator calls; a `n_iterations=100000` run drops from an estimated about 1 hour to **about 3.5s** (first call) / **about 1s** (cache warm, e.g. across a noise-level binary search).

Both optimizations were verified for correctness against independent reference computations (noiseless QER = 0, matching statistics under noise, exact evolution cross-checked against `qiskit.quantum_info.Statevector`) before being adopted.

> **Note**: `results/` is unchanged from the published values --> only relocated, not recomputed. Spot-checking the exact method against a couple of hypercube $(P, t)$ points turned up values that didn't match the checked-in file; this needs the authors' own investigation (it may be a stale cache, a stopping-heuristic difference, or something else) before any result file is regenerated. Treat `sweep_min_c` as a fast, exact *tool* available for that investigation, not as something that has already replaced the official numbers.

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
