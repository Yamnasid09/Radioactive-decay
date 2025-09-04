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
from .plotting import plot_counts, plot_log_counts, plot_activity, plot_measured_counts

# Command-line tool to run simulations and save outputs


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def cmd_run(args):
    cfg = load_config(args.config)

    # Detector configuration (optional)
    det_cfg = (cfg.get("detector", {}) or {})
    eff = float(det_cfg.get("efficiency", 1.0))
    noise = str(det_cfg.get("noise", "none")).lower()

    rng = np.random.default_rng(cfg.get("random_seed", 0))
    dt, T = float(cfg["dt"]), float(cfg["T"])
    simcfg = SimConfig(
        dt=dt,
        T=T,
        n_realizations=int(cfg["monte_carlo"]["n_realizations"]),
        engine=str(cfg["monte_carlo"].get("engine", "binomial")),
    )

    isotopes = [
        Isotope(
            d["name"],
            int(d["N0"]),
            half_life=d.get("half_life"),
            lam=d.get("lambda"),
        )
        for d in cfg["isotopes"]
    ]

    run_id = time.strftime("%Y%m%d-%H%M%S")
    rn = cfg.get("run_name", "").strip()
    if rn:
        run_id = f"{run_id}-{rn}"

    outdir = Path(cfg.get("output_dir", "data")) / run_id
    ensure_dir(outdir)

    # Save run metadata
    with open(outdir / "meta.json", "w") as f:
        json.dump({"config": cfg, "run_id": run_id}, f, indent=2)

    records = []
    for iso in isotopes:
        # ---- Simulation
        t, traj = simulate_isotope(iso, simcfg, rng)
        meanN, ci = mean_and_ci(traj)
        lam_hat, N0_hat, r2 = fit_lambda_from_counts(t, meanN)

        # ---- Save counts CSV
        pd.DataFrame({"t": t, "N_mean": meanN, "N_ci": ci}).to_csv(
            outdir / f"counts_{iso.name}.csv", index=False
        )

        # ---- Plots
        plot_counts(
            t,
            meanN,
            ci,
            label=f"{iso.name}",
            path=outdir / f"counts_{iso.name}.png",
            show=bool(cfg["plots"]["show"]),
        )
        plot_log_counts(
            t,
            meanN,
            label=f"{iso.name}",
            path=outdir / f"log_counts_{iso.name}.png",
            show=bool(cfg["plots"]["show"]),
        )

        # ---- Optional detector measurement (per time bin)
        if eff < 1.0 or noise != "none":
            # Expected decays between bins from the mean trajectory
            decays = np.maximum(meanN[:-1] - meanN[1:], 0.0)
            expected_detected = eff * decays

            if noise == "poisson":
                measured = rng.poisson(expected_detected)
            else:
                measured = expected_detected  # noiseless

            # Save per-bin measured counts (aligned with t[1:])
            pd.DataFrame({"t": t[1:], "measured_counts": measured}).to_csv(
                outdir / f"measured_counts_{iso.name}.csv", index=False
            )
            plot_measured_counts(
                t[1:],
                measured,
                label=f"{iso.name}",
                path=outdir / f"measured_counts_{iso.name}.png",
                show=bool(cfg["plots"]["show"]),
            )

        # ---- Fit report
        with open(outdir / f"fit_{iso.name}.txt", "w") as f:
            f.write(f"lambda_hat={lam_hat:.6f}\n")
            f.write(f"T12_hat={np.log(2) / lam_hat:.6f}\n")
            f.write(f"N0_hat={N0_hat:.1f}\n")
            f.write(f"R2={r2:.5f}\n")

        records.append(
            {
                "isotope": iso.name,
                "lam_true": iso.lam,
                "lam_hat": lam_hat,
                "T12_true": iso.half_life,
                "T12_hat": np.log(2) / lam_hat,
                "R2": r2,
            }
        )

    # ---- Analytical mixture (no MC)
    N_mix, A_mix = [], []
    for tt in t:
        N, A = mixture_counts_analytical(isotopes, tt)
        N_mix.append(N)
        A_mix.append(A)

    pd.DataFrame({"t": t, "N": N_mix, "A": A_mix}).to_csv(
        outdir / "mixture_analytical.csv", index=False
    )
    plot_activity(
        t,
        np.array(A_mix),
        label="mixture",
        path=outdir / "activity_mixture.png",
        show=bool(cfg["plots"]["show"]),
    )

    # ---- Summary CSV
    pd.DataFrame.from_records(records).to_csv(outdir / "summary_fits.csv", index=False)

    # ---- Update "latest" pointer
    latest = Path(cfg.get("output_dir", "data")) / "latest"
    try:
        if latest.exists() or latest.is_symlink():
            latest.unlink()
        latest.symlink_to(outdir, target_is_directory=True)
    except Exception:
        with open(Path(cfg.get("output_dir", "data")) / "LATEST_PATH.txt", "w") as f:
            f.write(str(outdir))

    print(f"Run complete. Outputs in {outdir}")


