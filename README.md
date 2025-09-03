# Radioactive Decay Simulation

# Radioactive Decay Simulation
![CI Status](https://github.com/Yamnasid09/Radioactive-decay/actions/workflows/tests.yml/badge.svg)
A clean, well-tested toolkit to simulate radioactive decay and reproduce the exponential law.


---

## 🔬 Physics Background
For a species with decay constant λ and half-life:

\[
T_{1/2} = \frac{\ln 2}{\lambda}
\]

The number of undecayed nuclei at time *t* is:

\[
N(t) = N_0 e^{-\lambda t}, \quad A(t)=\lambda N(t)
\]

In the Monte Carlo model, each nucleus decays in a small time step Δt with probability:

\[
p = 1 - e^{-\lambda \Delta t} \approx \lambda \Delta t
\]

---

## 🚀 Features
- **Two engines**: analytical model and Monte Carlo
- **Multi-isotope support** (mixtures, independent chains)
- **Config-driven runs** via YAML
- **Command-line interface (CLI)** for easy runs
- **Results saved** as CSV + plots (PNG)
- **Unit tests** with `pytest` for reliability

---

## ⚙️ Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/<your-username>/radioactive-decay.git
cd radioactive-decay
pip install -r requirements.txt
![Counts vs time — Tc99m](docs/counts_Tc99m.png)
![Log counts — Tc99m](docs/log_counts_Tc99m.png)

## 🔁 Reproducibility

Is repo ki figures ko bilkul waise hi dobara banane ke liye:

```bash
# env install
pip install -r requirements.txt

# run simulation (Tc99m, 24h window, 300 realizations)
python -m src.cli run --config config/default.yaml

# outputs yahan milenge (naya timestamp):
data/<run_id>/

# important files:
# - counts_Tc99m.png (N(t))
# - log_counts_Tc99m.png (log N vs t)
# - activity_mixture.png
# - fit_Tc99m.txt (lambda_hat, T12_hat, R2)
# - summary_fits.csv
## 🎤 Viva Checklist

- ✅ Repo overview: folder structure (`src/`, `config/`, `tests/`, `docs/`, `data/`)
- ✅ Physics recap: $N(t)=N_0 e^{-\lambda t}$, $T_{1/2}=\ln 2/\lambda$
- ✅ Install deps: `pip install -r requirements.txt`
- ✅ Tests run: `pytest -q` (explain what tests check)
- ✅ Simulation run: `python -m src.cli run --config config/default.yaml`
- ✅ Show outputs: `counts_Tc99m.png`, `log_counts_Tc99m.png`, `fit_Tc99m.txt` (T12_hat ≈ 21636 s)
- ✅ Config explain: `dt`, `T`, `n_realizations`, isotopes (Tc99m)
- ✅ Code tour: `decay.py`, `simulate.py`, `analysis.py`, `plotting.py`, `cli.py`
- ✅ Git usage: meaningful commits + tags (optional `v1.0.0`)
- ✅ CI proof: Actions “tests” badge is green
- ✅ Limitations & future work: detector noise, dead-time, decay chains, Numba/JAX

