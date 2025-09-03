import argparse
import json
import time
from pathlib import Path
import yaml
import numpy as np
import pandas as pd

from .decay import Isotope, mixture_counts_analytical
from .simulate import SimConfig, simulate_isotope
from .analysis import mean_and_ci, fit_lambda_from_counts
from .plotting import plot_counts, plot_log_counts, plot_activity


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def cmd_run(args):
    cfg = load_config(args.config)
    rng = np.random.default_rng(cfg.get("random_seed", 0))
    dt, T = cfg["dt"], cfg["T"]
    simcfg = SimConfig(dt=dt, T=T,
                       n_realizations=cfg["monte_carlo"]["n_realizations"],
                       engine=cfg["monte_carlo"].get("engine", "binomial"))

    isotopes = [Isotope(d["name"], d["N0"],
                        half_life=d.get("half_life"),
                        lam=d.get("lambda")) for d in cfg["isotopes"]]

    run_id = time.strftime("%Y%m%d-%H%M%S") + ("-" + cfg.get("run_name", ""))
    outdir = Path(cfg.get("output_dir", "data")) / run_id
    ensure_dir(outdir)

    # Save run metadata
    with open(outdir/"meta.json", "w") as f:
        json.dump({"config": cfg, "run_id": run_id}, f, indent=2)

    records = []
    for iso in isotopes:
        t, traj = simulate_isotope(iso, simcfg, rng)
        meanN, ci = mean_and_ci(traj)
        lam_hat, N0_hat, r2 = fit_lambda_from_counts(t, meanN)

        # Save CSV
        df = pd.DataFrame({"t": t, "N_mean": meanN, "N_ci": ci})
        df.to_csv(outdir/f"counts_{iso.name}.csv", index=False)

        # Plots
        plot_counts(t, meanN, ci, label=f"{iso.name}",
                    path=outdir/f"counts_{iso.name}.png",
                    show=cfg["plots"]["show"])
        plot_log_counts(t, meanN, label=f"{iso.name}",
                        path=outdir/f"log_counts_{iso.name}.png",
                        show=cfg["plots"]["show"])

        # Fit report
        with open(outdir/f"fit_{iso.name}.txt", "w") as f:
            f.write(f"lambda_hat={lam_hat:.6f}\n")
            f.write(f"T12_hat={np.log(2)/lam_hat:.6f}\n")
            f.write(f"N0_hat={N0_hat:.1f}\n")
            f.write(f"R2={r2:.5f}\n")

        records.append({
            "isotope": iso.name,
            "lam_true": iso.lam,
            "lam_hat": lam_hat,
            "T12_true": iso.half_life,
            "T12_hat": np.log(2)/lam_hat,
            "R2": r2
        })

    # Analytical mixture
    N_mix, A_mix = [], []
    for tt in t:
        N, A = mixture_counts_analytical(isotopes, tt)
        N_mix.append(N)
        A_mix.append(A)
    dfm = pd.DataFrame(
