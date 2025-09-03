# Software & Computing Project — Radioactive Decay Simulator

**Repo:** https://github.com/Yamnasid09/Radioactive-decay  
**Docs (GitHub Pages):** https://Yamnasid09.github.io/Radioactive-decay/  
**Release:** v1.0.0  **CI:** passing (pytest)

## Overview
- Analytical model: \( N(t)=N_0 e^{-\lambda t} \), \( T_{1/2}=\ln 2/\lambda \)
- Monte Carlo simulation (binomial engine; optional Numba JIT engine)
- Config-driven runs (YAML), CLI, CSV outputs + PNG plots
- Example isotope: **Tc-99m** (half-life ≈ 21636 s)

## How to Reproduce
```bash
pip install -r requirements.txt
python -m src.cli run --config config/default.yaml
pytest -q
