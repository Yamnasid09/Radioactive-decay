import argparse, os, json, time
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt

# --------- models ---------

@dataclass
class ChainParams:
    N0A: int
    lamA: float
    lamB: float

def simulate_chain_deterministic(params: ChainParams, dt: float, T: float):
    t = np.arange(0.0, T + dt, dt)
    NA = params.N0A * np.exp(-params.lamA * t)
    # Handle lamA == lamB limit
    if abs(params.lamA - params.lamB) < 1e-12:
        NB = params.lamA * params.N0A * t * np.exp(-params.lamA * t)
    else:
        NB = (params.lamA * params.N0A) / (params.lamB - params.lamA) * (
            np.exp(-params.lamA * t) - np.exp(-params.lamB * t)
        )
    return t, NA.astype(float), NB.astype(float)

def simulate_chain_mc(params: ChainParams, dt: float, T: float, n_realizations: int, rng: np.random.Generator):
    pA = 1.0 - np.exp(-params.lamA * dt)
    pB = 1.0 - np.exp(-params.lamB * dt)
    t = np.arange(0.0, T + dt, dt)
    steps = t.size
    R = int(n_realizations)

    NA_traj = np.empty((R, steps), dtype=float)
    NB_traj = np.empty((R, steps), dtype=float)

    for r in range(R):
        NA = int(params.N0A)
        NB = 0
        NA_traj[r, 0] = NA
        NB_traj[r, 0] = NB
        for k in range(1, steps):
            decayA = rng.binomial(NA, pA) if NA > 0 else 0
            transfer = decayA
            NA -= decayA
            decayB = rng.binomial(NB, pB) if NB > 0 else 0
            NB = NB - decayB + transfer
            NA_traj[r, k] = NA
            NB_traj[r, k] = NB

    return t, NA_traj, NB_traj

# --------- saving helper ---------

def _save_run(arrays: dict, meta: dict, out="data/runs"):
    from pathlib import Path
    out_root = Path(out)
    out_root.mkdir(parents=True, exist_ok=True)
    run_dir = out_root / time.strftime("run_%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    for k, v in arrays.items():
        a = np.asarray(v)
        np.save(run_dir / f"{k}.npy", a)
        try:
            np.savetxt(run_dir / f"{k}.csv", a, delimiter=",")
        except Exception:
            pass

    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    last = out_root / "last"
    try:
        if last.exists() or last.is_symlink():
            last.unlink()
        last.symlink_to(run_dir.resolve())
    except Exception:
        with open(out_root / "last.txt", "w") as f:
            f.write(str(run_dir.resolve()))

    print(f"[OK] Saved chain results to: {run_dir}")
    return str(run_dir)

# --------- CLI ---------

def main():
    ap = argparse.ArgumentParser(description="A -> B decay chain (deterministic or Monte-Carlo)")
    ap.add_argument("--mode", choices=["deterministic", "mc"], default="mc")
    ap.add_argument("--n0a", type=int, required=True, help="Initial nuclei of A")
    ap.add_argument("--lambda-a", dest="lambda_a", type=float, required=True)
    ap.add_argument("--lambda-b", dest="lambda_b", type=float, required=True)
    ap.add_argument("--tmax", type=float, default=10.0)
    ap.add_argument("--dt", type=float, default=0.05)
    ap.add_argument("--realizations", type=int, default=30, help="MC only")
    ap.add_argument("--seed", type=int, default=123, help="MC only")
    ap.add_argument("--out", default="images", help="Where to save plots")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    params = ChainParams(N0A=args.n0a, lamA=args.lambda_a, lamB=args.lambda_b)

    if args.mode == "deterministic":
        t, NA, NB = simulate_chain_deterministic(params, args.dt, args.tmax)
        run_dir = _save_run(
            {"t": t, "NA": NA, "NB": NB},
            {"mode": "chain_deterministic", "n0a": args.n0a, "lambda_a": args.lambda_a, "lambda_b": args.lambda_b, "tmax": args.tmax, "dt": args.dt},
        )
    else:
        rng = np.random.default_rng(args.seed)
        t, NA_traj, NB_traj = simulate_chain_mc(params, args.dt, args.tmax, args.realizations, rng)
        NA = NA_traj.mean(axis=0)
        NB = NB_traj.mean(axis=0)
        run_dir = _save_run(
            {"t": t, "NA": NA, "NB": NB, "NA_traj": NA_traj, "NB_traj": NB_traj},
            {"mode": "chain_mc", "n0a": args.n0a, "lambda_a": args.lambda_a, "lambda_b": args.lambda_b, "tmax": args.tmax, "dt": args.dt, "n_realizations": args.realizations},
        )

    # quick plots
    plt.figure()
    plt.plot(t, NA, label="N_A(t)")
    plt.plot(t, NB, label="N_B(t)")
    plt.xlabel("Time"); plt.ylabel("Counts")
    plt.title("A -> B decay chain")
    plt.legend(); plt.grid(True, alpha=0.3); plt.tight_layout()
    plt.savefig(os.path.join(args.out, "chain_na_nb.png"), dpi=200)

    mA = NA > 0
    mB = NB > 0
    if mA.any():
        plt.figure()
        plt.plot(t[mA], np.log(NA[mA]), ".", label="ln N_A")
        if mB.any():
            plt.plot(t[mB], np.log(NB[mB]), ".", label="ln N_B")
        plt.xlabel("Time"); plt.ylabel("ln counts"); plt.legend()
        plt.grid(True, alpha=0.3); plt.tight_layout()
        plt.savefig(os.path.join(args.out, "chain_log.png"), dpi=200)

    print("[OK] Saved plots to", args.out)

if __name__ == "__main__":
    main()
