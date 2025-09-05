import argparse, os, json
import numpy as np
import matplotlib.pyplot as plt

def load_series(run_dir: str):
    t = np.load(os.path.join(run_dir, "t.npy"))
    series = None
    for cand in ("N.npy", "counts.npy"):
        p = os.path.join(run_dir, cand)
        if os.path.exists(p):
            series = np.load(p).astype(float)
            break
    if series is None:
        p = os.path.join(run_dir, "traj.npy")
        if os.path.exists(p):
            series = np.load(p).mean(axis=0).astype(float)
        else:
            raise SystemExit("No N.npy/counts.npy/traj.npy found in run dir.")
    meta = {}
    mpath = os.path.join(run_dir, "meta.json")
    if os.path.exists(mpath):
        with open(mpath) as f:
            meta = json.load(f)
    return t, series, meta

def main():
    ap = argparse.ArgumentParser(description="Add Poisson background to a saved run and plot")
    ap.add_argument("--run-dir", default="data/runs/last")
    ap.add_argument("--bg-rate", type=float, required=True, help="Background counts per time-bin (per dt).")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="images")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    t, N, meta = load_series(args.run_dir)
    bg = rng.poisson(args.bg_rate, size=N.shape)
    meas = N + bg

    plt.figure(); plt.plot(t, N, label="N(t) (clean)")
    plt.plot(t, meas, ".", label=f"with background (rate={args.bg_rate}/bin)")
    plt.xlabel("Time"); plt.ylabel("Counts")
    ttl = f"N(t) with background — {meta.get('mode','')}".strip(" -")
    plt.title(ttl); plt.legend(); plt.grid(True, alpha=0.3); plt.tight_layout()
    p1 = os.path.join(args.out, "nt_curve_bg.png"); plt.savefig(p1, dpi=200)

    mask = meas > 0
    plt.figure(); plt.plot(t[mask], np.log(meas[mask]), ".", label="log(measured)")
    plt.xlabel("Time"); plt.ylabel("ln Counts"); plt.title("Log counts with background")
    plt.grid(True, alpha=0.3); plt.tight_layout()
    p2 = os.path.join(args.out, "log_nt_bg.png"); plt.savefig(p2, dpi=200)

    print(f"[OK] Saved {p1} and {p2}")

if __name__ == "__main__":
    main()
